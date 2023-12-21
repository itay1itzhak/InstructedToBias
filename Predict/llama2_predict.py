import torch
import torch.nn.functional as F
from Predict.hugging_face_perdictor import HFPredictor

sm = torch.nn.LogSoftmax(dim=1)
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)


import os
from transformers import LlamaTokenizer, LlamaForCausalLM


class Llama2Predictor(HFPredictor):
    def load_model_and_tokenizer(
        self,
    ):
        model_name, _, cache_dir = self.set_device_and_cache_dir()

        model_name = f"meta-llama/{model_name}-hf"
        tokenizer = LlamaTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        # parallize the model
        model = LlamaForCausalLM.from_pretrained(
            model_name, cache_dir=cache_dir  # , device_map="auto"
        )

        # if pretrained llama2
        if "chat" not in model_name:
            # pretrained need to add pad token for batched label scoring
            tokenizer.add_special_tokens({"pad_token": "<pad>"})

            # Resize token embeddings
            model.config.pad_token_id = tokenizer.pad_token_id
            model.resize_token_embeddings(len(tokenizer))

        self.change_model_device(model)
        self.model = model
        self.tokenizer = tokenizer

    def get_scores_for_labels(self, input, labels):
        # concat labels to the corrposnded input text
        input_with_answers = [i + label for label in labels for i in input]

        # get labels tokens ids
        labels_tokens = self.tokenizer(labels, add_special_tokens=False)["input_ids"]

        # get the last token id of each label
        labels_tokens = [label[-1] for label in labels_tokens]

        # Get encodings for each input text to avoid padding
        input_enc = self.tokenizer.batch_encode_plus(
            input_with_answers,
            return_tensors="pt",
            # add_special_tokens=True,
            # truncation=True,
            padding="longest",
        )

        for k, v in input_enc.items():
            input_enc[k] = v.to(self.model.device)

        # Get model output logits
        model_output = self.model(**input_enc)

        # Compute the log probabilities associated with each of the labels
        labels_log_probs = F.log_softmax(model_output.logits, dim=-1)

        # Get the ids of the token before the last token before padding (to see the probablity of the last token given the one before the last token)
        before_padding_ids = (
            input_enc["input_ids"].ne(self.tokenizer.pad_token_id).sum(-1) - 2
        )

        # Collect labels scores from the -2 token in labels_log_probs (the one that predict the last token)
        # and collect for each line the id in labels_tokens
        labels_scores = labels_log_probs[:, before_padding_ids, labels_tokens]

        # Need just the diagonal of the matrix, as it the prob of the label for each line
        labels_scores = torch.diag(labels_scores)

        return labels_scores

    def get_generated_prediction(self, prompt):
        input_tokenized = self.tokenizer(
            prompt,
            return_tensors="pt",
        )
        if torch.cuda.is_available():
            input_tokenized = input_tokenized.to(self.model.device)

        outputs = self.model.generate(
            **input_tokenized,
            # max_new_tokens=5,
            return_dict_in_generate=True,
            output_scores=True,
            do_sample=False,
        )
        transition_scores = self.model.compute_transition_scores(
            outputs.sequences, outputs.scores, normalize_logits=True
        )

        input_length = input_tokenized.input_ids.shape[1]
        generated_tokens = outputs.sequences[:, input_length:]
        # decode the generated tokens
        generated_tokens_decoded = self.tokenizer.batch_decode(
            generated_tokens, skip_special_tokens=True
        )

        logits = [
            (self.tokenizer.decode(id.item()), p.item())
            for id, p in zip(generated_tokens[0], transition_scores[0])
        ]

        return generated_tokens_decoded[0].strip().strip("."), logits
