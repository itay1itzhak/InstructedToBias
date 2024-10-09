from abc import abstractmethod
import torch
import torch.nn.functional as F
import os

import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)


import numpy as np
import os
from Predict.Predictor import Predictor


class HFPredictor(Predictor):
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

    def set_parameters(self):
        super().set_parameters()
        self.load_model_and_tokenizer()

    @abstractmethod
    def load_model_and_tokenizer(
        self,
    ):
        pass

    @abstractmethod
    def get_scores_for_labels(self, input, labels):
        pass

    @abstractmethod
    def get_generated_prediction(
        self,
        prompt,
    ):
        pass

    def set_device_and_cache_dir(self):
        cwd = os.getcwd()
        cache_dir = cwd + "/huggingface/.cache"
        os.makedirs(cache_dir, exist_ok=True)

        model_name = self.parameters["engine"]
        logging.info(f"Loading model and tokenizer for {model_name}")
        if torch.cuda.is_available():
            device = torch.device("cuda")
        else:
            device = torch.device("cpu")
        logging.info(f"Using device {device}")

        return model_name, device, cache_dir

    def change_model_device(self, model):
        # if torch.cuda.is_available():
        #    model.to("cuda")
        if "cpu" in str(model.device):
            print(f"NO GPU! {model.device=}")
        else:
            print(f"Using GPU. {model.device=}")

    def get_maximum_logprobs_answer(
        self,
        prompt,
    ):
        labels = [t[0] for t in self.possible_answers]

        # Get the scores for each possible answer
        labels_scores = self.get_scores_for_labels([prompt], labels)

        if self.should_normalize:
            if not self.base_probs:
                # get base probs which are the last line of the prompt
                self.base_probs["base_probs"] = self.get_scores_for_labels(
                    [prompt.split("\n")[-1]], labels
                )

            labels_scores = labels_scores - self.base_probs["base_probs"]
        # Get the maximum score for each input
        max_scores = labels_scores.max(dim=-1)[0]
        # Get the index of the maximum score for each input
        max_scores_idx = labels_scores.argmax(dim=-1)
        # Get the answer corresponding to the maximum score
        max_scores_answers = self.possible_answers[max_scores_idx][0]
        # Get the log probability of the maximum score
        max_scores_logprobs = max_scores - labels_scores.logsumexp(dim=-1)
        # Get the normalized log probability of the maximum score
        # max_scores_logprobs_norm = max_scores_logprobs - max_scores_logprobs.logsumexp(dim=-1)

        return max_scores_answers, max_scores_logprobs.item()

    def predict(
        self,
        example,
        prompt,
    ):
        prediction = dict()
        prediction["input"] = prompt

        if self.possible_answers:
            prediction_text, prediction_log_probs = self.get_maximum_logprobs_answer(
                prompt,
            )
        else:  # return model completion
            prediction_text, prediction_log_probs = self.get_generated_prediction(
                prompt,
            )

        prediction["prediction"] = prediction_text
        metadata = example.copy()
        metadata["log_probs"] = prediction_log_probs

        prediction["metadata"] = metadata
        return prediction, metadata
