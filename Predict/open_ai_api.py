from dotenv import load_dotenv
import numpy as np
import openai
import os
import time
from retry import retry

from Data_generation.templates import get_possible_answers
from Predict.Predictor import Predictor


def _ms_since_epoch():
    return time.perf_counter_ns() // 1000000


class OpenAIPredictor(Predictor):
    def __init__(
        self,
        bias_name,
        engine,
        max_tokens,
        predict_according_to_log_probs,
        should_normalize,
        save_every_n_examples,
    ):
        super().__init__(
            bias_name,
            engine,
            max_tokens,
            predict_according_to_log_probs,
            should_normalize,
            save_every_n_examples,
        )
        self.min_ms_between_api_calls = 1000

    def set_parameters(self):
        super().set_parameters()
        self.time_of_last_api_call = _ms_since_epoch()
        self.add_openai_parameters(self.parameters)

        # to save time when running the cheaper models, we'll save every 1000 examples
        if self.save_every_n_examples < 1000 and (
            "curie" in self.engine or "babbage" in self.engine or "ada" in self.engine
        ):
            self.save_every_n_examples = 1000

    def add_openai_parameters(self, parameters):
        # openai API setup and parameters
        # openai.organization = YOUR_KEY_HERE
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")

        # openai.api_key = os.getenv("OPENAI_API_KEY")
        print(f"openai.api_key={openai.api_key}")

        parameters["top_p"] = 0  # greedy
        parameters["temperature"] = 1
        parameters[
            "logprobs"
        ] = 5  # maximal value accorrding to https://beta.openai.com/docs/api-reference/completions/create#completions/create-logprobs, used to be 10...

    def wait_between_predictions(self):
        # OpenAI limits us to 3000 calls per minute:
        # https://help.openai.com/en/articles/5955598-is-api-usage-subject-to-any-rate-limits
        # that is why the default value of self.min_ms_between_api_calls is 20
        if (
            cur_time := _ms_since_epoch()
        ) <= self.time_of_last_api_call + self.min_ms_between_api_calls:
            ms_to_sleep = self.min_ms_between_api_calls - (
                cur_time - self.time_of_last_api_call
            )
            time.sleep(ms_to_sleep / 1000)
        self.time_of_last_api_call = _ms_since_epoch()

    def get_token_index(self, all_tokens, ans):
        if ans.lower() in all_tokens:
            ans_index = len(all_tokens) - 1 - all_tokens[::-1].index(ans.lower())
        if ans in all_tokens:
            ans_index = len(all_tokens) - 1 - all_tokens[::-1].index(ans)
        return ans_index  # type:ignore

    def get_openai_ans_log_prob_given_domain(
        self,
        all_tokens,
        parameters,
    ):
        start_of_domain_token_index = (
            len(all_tokens) - 1 - all_tokens[::-1].index("\n") + 1
        )
        domain_text_with_ans = "".join(all_tokens[start_of_domain_token_index:])
        parameters["prompt"] = domain_text_with_ans
        self.time_of_last_api_call = _ms_since_epoch()
        self.wait_between_predictions()

        response_given_domain = openai.Completion.create(**parameters)
        all_tokens_given_domain = response_given_domain.choices[0][  # type:ignore
            "logprobs"
        ]["tokens"]
        all_tokens_probs_given_domain = response_given_domain.choices[0][  # type:ignore
            "logprobs"
        ]["token_logprobs"]

        ans_start_index_given_domain = all_tokens_given_domain.index("Answer") + 2
        ans_log_prob_given_domain = np.sum(
            all_tokens_probs_given_domain[ans_start_index_given_domain:]
        )

        return ans_log_prob_given_domain

    def get_openai_ans_log_prob(
        self,
        response,
        ans,
        ans_index,
        parameters,
    ):
        all_tokens = response.choices[0]["logprobs"]["tokens"]
        all_tokens_probs = response.choices[0]["logprobs"]["token_logprobs"]

        ans_index = -1  # index of the answer token
        ans_log_prob = all_tokens_probs[ans_index]

        if not self.should_normalize:
            return ans_log_prob
        #  see https://arxiv.org/pdf/2104.08315.pdf for normliziation method
        if ans not in self.base_probs:
            ans_log_prob_given_domain = self.get_openai_ans_log_prob_given_domain(
                all_tokens,
                parameters.copy(),
            )
            self.base_probs[ans] = ans_log_prob_given_domain  # type:ignore

        return ans_log_prob - self.base_probs[ans]  # type:ignore

    def get_openai_maximum_logprobs_answer(
        self,
        org_parameters,
    ):
        answers_with_probs = []
        for ans, ans_index in self.possible_answers:
            parameters = org_parameters.copy()
            parameters["max_tokens"] = 0
            parameters["prompt"] += ans
            self.time_of_last_api_call = _ms_since_epoch()
            self.wait_between_predictions()
            response = openai.Completion.create(**parameters)
            ans_log_prob = self.get_openai_ans_log_prob(
                response,
                ans,
                ans_index,
                parameters,
            )
            response["answer"] = ans  # type: ignore
            response["answer_log_prob"] = ans_log_prob  # type: ignore
            answers_with_probs.append((ans, response))
        # return the answer with the highest log_prob
        return max(answers_with_probs, key=lambda x: x[1]["answer_log_prob"])

    def predict_chat_sample_open_ai(
        self,
        example,
        prompt,
    ):
        parameters = self.parameters.copy()
        parameters["messages"] = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
        parameters["model"] = parameters["engine"]
        del parameters["engine"]
        del parameters["logprobs"]
        del parameters["prompt"]

        self.wait_between_predictions()

        response = openai.ChatCompletion.create(**parameters)
        prediction_text = (
            response.choices[0].message["content"].strip().strip(".")  # type:ignore
        )

        # build output data
        prediction = dict()
        prediction["input"] = prompt
        prediction["prediction"] = prediction_text  # type:ignore

        # build output metadata
        metadata = example.copy()  # dict()
        metadata["messages"] = parameters["messages"]  # type:ignore
        finish_reason = response.choices[0]["finish_reason"]  # type:ignore
        metadata["finish_reason"] = finish_reason
        metadata["index"] = response.choices[0]["index"]  # type:ignore

        prediction["metadata"] = metadata

        return prediction, metadata

    @retry(tries=10, delay=1, jitter=2, logger=None)
    def predict(
        self,
        example,
        prompt,
    ):
        if "gpt-4" in self.engine or "turbo" in self.engine:
            return self.predict_chat_sample_open_ai(
                example,
                prompt,
            )

        self.parameters["prompt"] = prompt

        self.wait_between_predictions()

        if self.possible_answers:
            self.parameters["echo"] = True
            prediction_text, response = self.get_openai_maximum_logprobs_answer(
                self.parameters,
            )
        else:  # return model completion
            response = openai.Completion.create(**self.parameters)
            prediction_text = response.choices[0].text.strip().strip(".")

        if response is None:
            raise Exception("Response from OpenAI API is None.")

        # build output data
        prediction = dict()
        prediction["input"] = prompt
        prediction["prediction"] = prediction_text

        # build output metadata
        metadata = example.copy()
        metadata["logprobs"] = response.choices[0]["logprobs"]
        finish_reason = response.choices[0]["finish_reason"]
        metadata["finish_reason"] = finish_reason
        # From the OpenAI API documentation it's not clear what "index" is, but let's keep it as well
        metadata["index"] = response.choices[0]["index"]

        prediction["metadata"] = metadata

        return prediction, metadata
