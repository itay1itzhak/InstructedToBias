from abc import ABC, abstractmethod
import time

from Data_generation.templates import (
    get_possible_answers,
)


class Predictor(ABC):
    def __init__(
        self,
        bias_name,
        engine,
        max_tokens,
        predict_according_to_log_probs,
        should_normalize,
        save_every_n_examples,
    ):
        self.bias_name = bias_name
        self.engine = engine
        self.max_tokens = max_tokens
        self.predict_according_to_log_probs = predict_according_to_log_probs
        self.should_normalize = should_normalize
        self.save_every_n_examples = save_every_n_examples
        self.base_probs = {}
        self.time_of_last_api_call = time.time()

    def set_parameters(self):
        parameters = {
            "engine": self.engine,
            "max_tokens": self.max_tokens,
        }

        self.parameters = parameters

        # choose possible answers
        if self.predict_according_to_log_probs:
            self.possible_answers = get_possible_answers(self.bias_name)
        else:
            self.possible_answers = None

        if self.should_normalize:
            self.base_probs = {}
        else:
            self.base_probs = None

    @abstractmethod
    def predict(self):
        raise NotImplementedError
