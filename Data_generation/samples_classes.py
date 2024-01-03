import copy
import itertools
import json
import logging
import os
import sys

sys.path.append("./")
from enum import Enum
from pathlib import Path

from Data_generation.templates import *
from tqdm.auto import tqdm


from utils import get_data_dir_and_file_name

logging.basicConfig(level=logging.INFO)


class Decoy_type(Enum):
    """
    Decoy types for the decoy effect bias. See decoy paper for explanation of the names
    """

    F = 1  # decoy is lower only in dim 1 of product compared to target
    R = 2  # decoy is lower only in dim 2 of product compared to target
    RF = 3  # decoy is lower in both dim 1 and 2 of product compared to target
    R_EXTREAM = 4  # decoy is exreamly lower only in dim 2 of product compared to target

    TWO_OPTIONS = 5  # for samples with no decoy at all


class Certainty_type(Enum):
    """
    Different type of certainty bias. See certainty paper for explanation of the names
    """

    DEVIDE_OPTION_A_TO_THREE_PROBS = 1
    DEVIDE_OPTION_A_TO_TWO_PROBS = 2
    NOT_PROBABLE = 3


class Belief_type(Enum):
    """
    False Belief types for the belief bias effect. See false belief paper for explanation of the names
    """

    EXP_DM_1 = 1  # To use data genereated using the method described in the paper
    EXP_DM_2 = 2  # To use data genereated using the method described in the paper
    EXP_DM_FULL = 3  # To use with the full deepmind dataset given as a file


class Sample:
    def __init__(
        self,
        bias_name: str,
        template: int,
        values: dict,
        with_bias,
    ):
        self.bias_name = bias_name
        self.template = template
        self.values = values
        self.with_bias = with_bias
        self.bias_type = values["bias_type"]

    def get_template_text(self):
        # Decoy
        if self.bias_name == "decoy" and self.bias_type == Decoy_type.TWO_OPTIONS:
            return ALL_DECOY_TEMP_TWO_OPTIONS[self.template]
        elif self.bias_name == "decoy" and self.bias_type != Decoy_type.TWO_OPTIONS:
            return ALL_DECOY_TEMP_THREE_OPTIONS[self.template]

        # certainty
        elif self.bias_name == "certainty":
            return CERTAINTY_TEMPLATES["CERTAINTY_BIAS_MEGA"][self.template]

        # False Belief
        elif self.bias_name == "false_belief":
            return ALL_FALSE_BELIEF_DEEPMIND_TEMP[self.template]
        else:
            raise Exception(
                f"Unexpected bias name, type and with_bias combination - {self.bias_name}, {self.bias_type}, with_bias={self.with_bias}"
            )

    def get_text(self):
        template_text = self.get_template_text()
        result = None
        if self.bias_name == "decoy":
            # hack for frying_pan
            if "frying_pan" in self.values["product"]:
                product = self.values["product"].replace("frying_pan", "frying pan")
            else:
                product = self.values["product"]
            if self.bias_type == Decoy_type.TWO_OPTIONS:
                result = template_text.substitute(
                    PRODUCT=product.split("_")[
                        0
                    ],  # for _cheaper #self.values["product"].split("_")[0],
                    PRODUCT_TYPE=self.values["product_type"],
                    PRODUCT_TYPEs=self.values["product_type"] + "s",
                    PRODUCT_TYPE_UPPERCASE=self.values["product_type"][0].upper()
                    + self.values["product_type"][1:],
                    PACKAGE=self.values["package"],
                    QUALITY_MEASURE=self.values["quality_measurment"],
                    PRICE1=self.values["price1"],
                    QUALITY1=self.values["quality1"],
                    PRICE2=self.values["price2"],
                    QUALITY2=self.values["quality2"],
                )
            else:
                result = template_text.substitute(
                    PRODUCT=product.split("_")[0],
                    PRODUCT_TYPE=self.values["product_type"],
                    PRODUCT_TYPEs=self.values["product_type"] + "s",
                    PRODUCT_TYPE_UPPERCASE=self.values["product_type"][0].upper()
                    + self.values["product_type"][1:],
                    PACKAGE=self.values["package"],
                    QUALITY_MEASURE=self.values["quality_measurment"],
                    PRICE1=self.values["price1"],
                    QUALITY1=self.values["quality1"],
                    PRICE2=self.values["price2"],
                    QUALITY2=self.values["quality2"],
                    PRICE3=self.values["price3"],
                    QUALITY3=self.values["quality3"],
                )
        elif self.bias_name == "certainty":
            result = template_text.safe_substitute(
                FIRST_OPTION=self.values["option_a"]["option_text"],  # first_option,
                SECOND_OPTION=self.values["option_b"]["option_text"],
                # OPENING_LINE=self.values["opening_line"],
                # CLOSING_LINE=self.values["closing_line"],
                FIRST_OPTION_OPENING=self.values["first_option_opening"],
                SECOND_OPTION_OPENING=self.values["second_option_opening"],
            )

        elif self.bias_name == "false_belief":
            result = template_text.substitute(
                PREMISE1=self.values["premise_1"],
                PREMISE2=self.values["premise_2"],
                CONCLUSION=self.values["conclusion"],
                CLOSING_LINE=self.values["closing_line"],
            )
        else:
            raise Exception("Not supported bias name in print!")

        if "-1" in result:
            raise Exception(f"-1 was found in text! {result}")

        return result

    def get_dict_for_json(self):
        json_dict = copy.deepcopy(self.values)
        json_dict["bias_name"] = self.bias_name
        json_dict["template"] = self.template
        json_dict["with_bias"] = self.with_bias
        json_dict["bias_type"] = str(self.bias_type)
        json_dict["text"] = self.get_text()

        return json_dict

    def __str__(self) -> str:
        return str(self.get_text())


class SamplesGen:
    def __init__(
        self,
        bias_name: str,
        templates: list[int],
        values: list[dict],
        bias_types,
        with_bias=True,
    ):
        self.bias_name = bias_name
        self.templates = templates
        self.values = values
        self.with_bias = with_bias
        self.bias_types = bias_types

    def verify_valid_bias_name(self):
        valid_bias_names = ["decoy", "certainty", "false_belief"]

        if self.bias_name not in valid_bias_names:
            raise Exception(
                f"Invalid bias name! Allowed bias names: {', '.join(valid_bias_names)}, bias_name={self.bias_name}"
            )

    def generate_samples(self):
        samples = []
        self.verify_valid_bias_name()

        all_comb = list(
            itertools.product(
                self.templates,
                self.values,
            )
        )

        for cur_comb in all_comb:
            samples.append(Sample(self.bias_name, *cur_comb, self.with_bias))

        return samples


@staticmethod
def print_samples(samples):
    for s in samples:
        print(">" * 130)
        print(s)
    print(f"{len(samples)}")


@staticmethod
def write_samples_to_path(
    samples: list[Sample],
    path: Path,
    bias_name: str,
    bias_types: str,
    templates: list[int],
    with_bias: bool,
    product: str,
    all_options_permutations: bool,
    overwrite=True,
):
    all_samples_dicts = dict()
    for i, s in enumerate(samples):
        all_samples_dicts[i] = s.get_dict_for_json()
    json_object = json.dumps(all_samples_dicts, indent=4)

    dir_name, file_name = get_data_dir_and_file_name(
        path,
        bias_name,
        bias_types,
        templates,
        with_bias,
        product,
        all_options_permutations,
    )

    output_file = dir_name.joinpath(file_name)

    if overwrite or not os.path.exists(file_name):
        with open(output_file, "w") as outfile:
            outfile.write(json_object)

    logging.info(f"Wrote file:{file_name}\nIn dir: {dir_name}")
