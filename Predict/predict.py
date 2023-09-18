import argparse
import json
import logging

from Predict.open_ai_api import OpenAIPredictor
from Predict.t5_predict import T5Predictor


logging.basicConfig(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)
import os
import random

random.seed(42)
from pathlib import Path

from Data_generation.templates import get_possible_answers

from Predict.few_shots import *
from utils import OPENAI_MODELS, T5_MODELS, get_prediction_output_files_names


def init_or_load_from_existing_predictions(
    overwrite_existing_predictions, output_path, output_with_metadata_path, len_examples
):
    id_to_start_predictions_from = 0

    # load existing predictions if exist, otherwise create a new dict
    if overwrite_existing_predictions or not output_path.is_file():
        predictions = dict()
    else:
        with open(output_with_metadata_path) as preexisting_predictions_f:
            # we use `output_with_metadata_path` here and not `output` as in this method
            # `predictions` include the metadata.
            predictions = json.load(preexisting_predictions_f)
        # get the first id we should start to predict from
        n_preexisting_predictions = len(predictions)
        id_to_start_predictions_from = n_preexisting_predictions + 1

        # check if we already generated all the predictions
        if 0 < n_preexisting_predictions < len_examples:  # len(examples):
            logging.info(
                f"{output_path} already contains the first {n_preexisting_predictions} predictions. starting to generate predictions from id {id_to_start_predictions_from}"
            )
        elif n_preexisting_predictions == len_examples:  # len(examples):
            logging.info(
                f"{output_path} already contains all {len_examples} predictions. to overwrite, set overwrite_existing_predictions=True"
            )
    return id_to_start_predictions_from, predictions


def update_progress(
    current_id,
    log_progress_every_n_examples,
    save_every_n_examples,
    bias_name,
    engine,
    output_path,
    output_with_metadata_path,
    predictions,
):
    # print progress
    if current_id % log_progress_every_n_examples == 0:
        logging.info(
            f"generated predictions up to id {current_id} for {bias_name} using the {engine} model"
        )
    # save predictions
    if current_id % save_every_n_examples == 0:
        # save the predictions with the metadata
        with open(output_with_metadata_path, "w+") as f_predictions_with_metadata:
            json.dump(predictions, f_predictions_with_metadata, indent=2)
        # save the predictions without the metadata
        predictions_without_metadata = dict()
        for id_ in predictions:
            predictions_without_metadata[id_] = dict()
            for field_name in predictions[id_]:
                if field_name != "metadata":
                    predictions_without_metadata[id_][field_name] = predictions[id_][
                        field_name
                    ]
            with open(output_path, "w+") as f_predictions:
                json.dump(predictions_without_metadata, f_predictions, indent=2)

        logging.info(
            f"saved predictions up to id {current_id} for {bias_name} using {engine}"
        )


def load_bias_data(
    bias_name, data_path, with_format_few_shot, with_task_few_shot, k_shot=2
):
    # if not with_format_few_shot and not with_task_few_shot:
    if with_format_few_shot or with_task_few_shot:
        all_temps, options, all_values = get_few_shots_temp_and_options(
            bias_name, data_path, with_format_few_shot
        )
    else:
        all_temps = [None]
        options = [None]
        all_values = [None]

    with open(data_path) as f_examples:
        examples = json.load(f_examples)

    if with_format_few_shot or with_task_few_shot and k_shot > 0:
        for e in examples.values():
            few_shots_texts = get_few_shot_text(
                with_format_few_shot,
                with_task_few_shot,
                e,
                examples,
                k_shot,
                bias_name,
                all_temps,
                all_values,
                options,
            )
            few_shot_text = "\n\n".join(few_shots_texts) + "\n\n"
            e["text"] = few_shot_text + e["text"]
    return examples


def print_prediction_info(
    examples, bias_name, engine, data_path, output_path, predict_according_to_log_probs
):
    logging.info("=" * 40)
    k = random.choice(list(examples.keys()))
    logging.info(examples[k]["text"])
    logging.info("=" * 40)

    logging.info(f"generating predictions for {bias_name} with model {engine}")
    logging.info(f"input path:\n{data_path}")
    logging.info(f"output path:\n{output_path}")
    if predict_according_to_log_probs:
        logging.info(
            f"Predicting according to max log prob with these possible answers: {get_possible_answers(bias_name)}"
        )


def save_remaining_unsaved_predictions(
    predictions,
    output_path,
    output_with_metadata_path,
    id_to_start_predictions_from,
    save_every_n_examples,
):
    n_generated_predictions = len(predictions) - id_to_start_predictions_from + 1
    if n_generated_predictions % save_every_n_examples != 0:
        with open(output_with_metadata_path, "w+") as f_predictions_with_metadata:
            json.dump(predictions, f_predictions_with_metadata, indent=2)

        for id_ in predictions:
            del predictions[id_]["metadata"]
        with open(output_path, "w+") as f_predictions:
            json.dump(predictions, f_predictions, indent=2)


def save_to_predictions(predictions, id_, prediction, metadata, examples):
    predictions[id_] = prediction.copy()
    predictions[id_]["metadata"] = metadata
    predictions[id_]["human_or_right_answer"] = examples[id_]["human_or_right_answer"]


def generate_all_predictions(
    bias_name: str,
    engine: str,
    max_tokens: int = -1,
    data_path: Path = Path("./Data"),
    predictions_dir: Path = Path("./Predictions"),
    overwrite_existing_predictions=False,
    min_ms_between_api_calls: int = 10,
    log_progress_every_n_examples: int = 1,
    save_every_n_examples: int = 10,
    predict_according_to_log_probs=False,
    should_normalize=False,
    with_format_few_shot=False,
    with_task_few_shot=False,
    k_shot=0,
    bias_types="all",
    templates="[1, 2, 3, 4, 5]",
    with_bias=True,
    product="",
    all_options_permutations=False,
):
    # load data with few shot if needed
    examples = load_bias_data(
        bias_name,
        data_path,
        with_format_few_shot,
        with_task_few_shot,
        k_shot=k_shot,
    )

    # define prediction output files paths
    output_path, output_with_metadata_path = get_prediction_output_files_names(
        predictions_dir,
        data_path,
        bias_name,
        engine,
        predict_according_to_log_probs,
        should_normalize,
        with_format_few_shot,
        with_task_few_shot,
        k_shot,
        bias_types,
        templates,
        with_bias,
        product,
        all_options_permutations,
    )

    # print some data about the prediction
    print_prediction_info(
        examples,
        bias_name,
        engine,
        data_path,
        output_path,
        predict_according_to_log_probs,
    )

    # check if we already have some predictions
    # (e.g. if the openai API failed before finishing to generate predictions for all examples)
    id_to_start_predictions_from, predictions = init_or_load_from_existing_predictions(
        overwrite_existing_predictions,
        output_path,
        output_with_metadata_path,
        len(examples),
    )

    # set predictor mode for the prediction
    if engine in OPENAI_MODELS:
        predictor = OpenAIPredictor(
            bias_name,
            engine,
            max_tokens,
            predict_according_to_log_probs,
            should_normalize,
            save_every_n_examples,
        )
    else:
        predictor = T5Predictor(
            bias_name,
            engine,
            max_tokens,
            predict_according_to_log_probs,
            should_normalize,
            save_every_n_examples,
        )

    predictor.set_parameters()

    predictor.save_every_n_examples = min(save_every_n_examples, len(examples))
    for id_str in range(id_to_start_predictions_from, len(examples)):
        id_str = str(id_str)
        prompt = examples[id_str]["text"]
        predictor.parameters["prompt"] = prompt

        prediction, metadata = predictor.predict(
            examples[id_str],
            prompt,
        )

        save_to_predictions(predictions, id_str, prediction, metadata, examples)

        update_progress(
            int(id_str),
            log_progress_every_n_examples,
            save_every_n_examples,
            bias_name,
            engine,
            output_path,
            output_with_metadata_path,
            predictions,
        )

    # save remaining unsaved predictions (if any)
    save_remaining_unsaved_predictions(
        predictions,
        output_path,
        output_with_metadata_path,
        id_to_start_predictions_from,
        save_every_n_examples,
    )

    logging.info(
        f"finished generating predictions for all {len(examples)} examples of {bias_name} using {engine}"
    )


def run_main(args):
    logging.info(f"Predicting samples for {args.bias_name}...")
    logging.info("=" * 80)

    generate_all_predictions(vars(args))

    logging.info("=" * 80)
    logging.info("All Done!")


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--dest_path", type=str, default="Predictions/", help="")

    parser.add_argument(
        "--bias_name",
        type=str,
        default="decoy",
        help="Which bias to use from all biases: decoy, certainty, false_belief.",
    )

    parser.add_argument(
        "--engine",
        type=str,
        default="text-davinci-002",
        # default="text-curie-001",
        help="Which model to use.",
    )
    parser.add_argument(
        "--max_tokens",
        type=int,
        default=20,
        help="How many tokens the model can output.",
    )
    parser.add_argument(
        "--overwrite_existing_predictions",
        default=False,
        action="store_true",
        help="If set to true, samples with same names that already exist will be overwritten.",
    )
    parser.add_argument(
        "--predict_according_to_log_probs",
        default=False,
        action="store_true",
        help="If set to true, The prediction will be done not by letting the model compelet the prompt, but to measure the probablity log-likelihood of each possible answer.",
    )
    parser.add_argument(
        "--should_normalize_log_prob",
        default=False,
        action="store_true",
        help="If set to true, The prediction log prob will be normlized accoridng the last line in the prompt, which is assumed to be the domain. Answer:  for asnwering questions for example.",
    )

    parser.add_argument(
        "--with_format_few_shot",
        default=False,
        action="store_true",
        help="If set to true, append to each example a k shot examples of the same format, with unrelated content.",
    )
    parser.add_argument(
        "--with_task_few_shot",
        default=False,
        action="store_true",
        help="If set to true, append to each example a k shot examples of the same task.",
    )
    parser.add_argument(
        "--k_shot",
        type=int,
        default=2,
        help="How many few-shot to use.",
    )

    parser.add_argument(
        "--data_path",
        type=str,
        default="Data/sample.json",
        help="File path in json format.",
    )

    parser.add_argument(
        "--bias_types",
        type=str,
        default="all",
        help="Types of bias. For decoy: only_two_options, or all.",
    )
    parser.add_argument(
        "--templates",
        type=str,
        default="1,2,3,4,5",
        help="Which templates to use from the templates.py file.",
    )
    parser.add_argument(
        "--with_bias",
        default=False,
        action="store_true",
        help="Are the created samples should be with bias, or unbiased versions.",
    )
    parser.add_argument(
        "--product",
        type=str,
        default="",
        help="For decoy bias only. Could be beer, car or phone.",
    )
    parser.add_argument(
        "--all_options_permutations",
        default=False,
        action="store_true",
        help="If set to true, samples will be created with all possible permutaitons for options position.",
    )
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()
    run_main(args)
