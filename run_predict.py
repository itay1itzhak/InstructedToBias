import itertools
import logging
import argparse
from Data_generation.templates import ALL_DECOY_PRODUCTS

from Predict.predict import generate_all_predictions
from utils import get_bias_type_templates_defaults

# the following models are tuned on instructions and will predict according generated text
INSTURCT_MODELS = [
    "text-davinci-002",
    "text-davinci-003",
    "flan-t5-xl",
    "flan-t5-xxl",
    "flan-t5-small",
    "gpt-4-0314",
    "gpt-4",
]

# the following models are vanilla and will predict according to log probs
VANILLA_MODELS = [
    "davinci",
    "t5-v1_1-small",
    "t5-v1_1-xl",
    "t5-v1_1-xxl",
    "t5-11b",
    "t5-small",
    "llama-7b",
    "llama-13b",
]


def set_experiment_args(
    bias_name,
    input_file,
    engine,
    should_normalize,
    overwrite_existing_predictions,
    k_shot,
    predict_instruct_according_to_log_probs,
    with_few_shot_task_or_format,
):
    """
    sets the experiment args for the current experiment
    """
    experiment_args = {
        "bias_name": bias_name,
        "data_path": input_file,
        "engine": engine,
        "should_normalize": should_normalize,
        "overwrite_existing_predictions": overwrite_existing_predictions,
    }

    # set few-shot args (if k_shot == 0, then no few-shot)
    if with_few_shot_task_or_format == "format":
        experiment_args["with_format_few_shot"] = True if k_shot != 0 else False
        experiment_args["with_task_few_shot"] = False
    else:
        experiment_args["with_format_few_shot"] = False
        experiment_args["with_task_few_shot"] = True if k_shot != 0 else False

    # set specific args for instruct or vanilla models
    if experiment_args["engine"] in INSTURCT_MODELS:
        experiment_args[
            "predict_according_to_log_probs"
        ] = predict_instruct_according_to_log_probs

        experiment_args["k_shot"] = k_shot

        # mostly no need for large max tokens for instruct models
        experiment_args["max_tokens"] = 20

        # but for gpt-4-0314, gpt-4, and turbo, we need more tokens in case they end up with a long answer
        if (
            experiment_args["engine"] == "gpt-4-0314"
            or experiment_args["engine"] == "gpt-4"
            or experiment_args["engine"] == "text-davinci-002"
            or "turbo" in experiment_args["engine"]
        ):
            experiment_args["max_tokens"] = 600
    # vanilla models
    else:
        experiment_args["predict_according_to_log_probs"] = True
        experiment_args["k_shot"] = k_shot
        experiment_args["max_tokens"] = 0

    if experiment_args["engine"] in [
        "davinci",
        "text-davinci-002",
        "text-davinci-003",
    ]:
        experiment_args["save_every_n_examples"] = 100
    # gpt4 is slow, so we save every 10 examples
    elif experiment_args["engine"] in ["gpt-4-0314", "gpt-4"]:
        experiment_args["save_every_n_examples"] = 10

    # for everything else, we save every 1000 examples
    else:
        experiment_args["save_every_n_examples"] = 1000

    return experiment_args


def run_predict_all(
    bias_name,
    bias_types,
    products,
    templates,
    overwrite_existing_predictions,
    all_k_shot_vanilla,
    all_k_shot_instruct,
    all_should_normalize_vanilla,
    all_models,
    all_predict_instruct_according_to_log_probs,
    all_should_normalize_instruct,
    with_few_shot_task_or_format,
):
    all_input_files = get_input_files_names(bias_name, products, templates, bias_types)

    # predict across all models, input files, k-shot, and should_normalize
    for engine in all_models:
        logging.info("+" * 20 + " " + engine + " " + "+" * 20)
        for input_file in all_input_files:
            logging.info("-" * 20 + " " + input_file + " " + "-" * 20)
            for (
                predict_instruct_according_to_log_probs
            ) in all_predict_instruct_according_to_log_probs:
                # align k-shot and should_normalize to the correct model type
                if engine in VANILLA_MODELS:
                    all_k_shot = all_k_shot_vanilla
                    all_should_normalize = all_should_normalize_vanilla
                else:
                    all_k_shot = all_k_shot_instruct
                    if predict_instruct_according_to_log_probs:
                        all_should_normalize = all_should_normalize_instruct
                    else:
                        all_should_normalize = [False]

                for k_shot, should_normalize in itertools.product(
                    all_k_shot, all_should_normalize
                ):
                    experiment_args = set_experiment_args(
                        bias_name,
                        input_file,
                        engine,
                        should_normalize,
                        overwrite_existing_predictions,
                        k_shot,
                        predict_instruct_according_to_log_probs,
                        with_few_shot_task_or_format,
                    )
                    try:
                        for k, v in experiment_args.items():
                            logging.info(f"{k} = {v}")
                        logging.info("=====================================")
                        generate_all_predictions(**experiment_args)
                    except Exception as e:
                        engine = experiment_args["engine"]
                        logging.info(
                            f"Did not predict file = {input_file}\nengine={engine}"
                        )
                        logging.info(e)
                        raise e


def get_input_files_names(bias_name, products, templates, bias_types):
    """
    return all input files names for a given bias and product
    """

    prefix = f"Data/{bias_name}"

    # default values
    bias_types, templates = get_bias_type_templates_defaults(
        bias_name, bias_types, templates
    )

    if bias_name == "decoy":
        if products is None:
            products = ALL_DECOY_PRODUCTS
        else:
            products = products.split(",")

        all_input_files = []
        for cur_product in products:
            all_input_files += [
                f"{prefix}/{cur_product}/all_permutations/t_{templates}_{bias_types}_Control.json",
                f"{prefix}/{cur_product}/all_permutations/t_{templates}_{bias_types}_Treatment.json",
            ]

    else:
        all_input_files = [
            f"{prefix}/all_permutations/t_{templates}_{bias_types}_Control.json",
            f"{prefix}/all_permutations/t_{templates}_{bias_types}_Treatment.json",
        ]

    return all_input_files


def parse_args(args):
    if args.all_models:
        all_models = args.all_models.split(",")
    else:
        all_models = []

    all_k_shot_vanilla = [int(k) for k in args.all_k_shot_vanilla.split(",")]
    all_k_shot_instruct = [int(k) for k in args.all_k_shot_instruct.split(",")]
    all_should_normalize_vanilla = [
        k == "True" for k in args.all_should_normalize_vanilla.split(",")
    ]

    all_predict_instruct_according_to_log_probs = [
        k == "True" for k in args.all_predict_instruct_according_to_log_probs.split(",")
    ]

    all_should_normalize_instruct = [
        k == "True" for k in args.all_should_normalize_instruct.split(",")
    ]

    return {
        "bias_name": args.bias_name,
        "bias_types": args.bias_types,
        "products": args.products,
        "templates": args.templates,
        "overwrite_existing_predictions": args.overwrite_existing_predictions,
        "with_few_shot_task_or_format": args.with_few_shot_task_or_format,
        "all_k_shot_vanilla": all_k_shot_vanilla,
        "all_k_shot_instruct": all_k_shot_instruct,
        "all_should_normalize_vanilla": all_should_normalize_vanilla,
        "all_models": all_models,
        "all_predict_instruct_according_to_log_probs": all_predict_instruct_according_to_log_probs,
        "all_should_normalize_instruct": all_should_normalize_instruct,
    }


def run_main(args):
    logging.info(f"Predicting samples for {args.bias_name}...")
    logging.info("\n" + "=" * 80 + "\n")

    parsed_args = parse_args(args)

    logging.info(f"\n{parsed_args = }\n")
    run_predict_all(**parsed_args)

    logging.info("\n" + "=" * 80 + "\n")
    logging.info("All Done!")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bias_name",
        type=str,
        default="decoy",
        help="Which bias to use from all biases: decoy, certainty, false_belief.",
    )
    parser.add_argument(
        "--all_models",
        type=str,
        default=None,
        help="Which models to use.",
    )
    parser.add_argument(
        "--products",
        type=str,
        default=None,
        help="Which products in decoy bias seperated by comma to predict (part of prediction file name). default is all products",
    )

    parser.add_argument(
        "--templates",
        type=str,
        default=None,
        help="Which templates to predict (part of prediction file name).",
    )

    parser.add_argument(
        "--bias_types",
        type=str,
        default=None,
        help="Which bias_types to predict (part of prediction file name). default is 'all' for decoy, 'three_probs,two_probs' for certainty, 'dm_1,dm_2' for false_belief",
    )

    parser.add_argument(
        "--overwrite_existing_predictions",
        default=False,
        action="store_true",
        help="If set to true, samples with same names that already exist will be overwritten.",
    )

    parser.add_argument(
        "--all_k_shot_vanilla",
        type=str,
        default="0",
        help="Which k-shot condition to use on the vanila models.",
    )
    parser.add_argument(
        "--all_k_shot_instruct",
        type=str,
        default="0",
        help="Which k-shot condition to use on the instructions tuned models.",
    )
    parser.add_argument(
        "--all_should_normalize_vanilla",
        type=str,
        default="True",
        help="Should normlize vanile answers according to log prob, not, or both.",
    )

    parser.add_argument(
        "--all_predict_instruct_according_to_log_probs",
        type=str,
        default="False",
        help="Should instruction models answer according to log prob, not, or both.",
    )

    parser.add_argument(
        "--all_should_normalize_instruct",
        type=str,
        default="True",
        help="Should normlize insturct models answers according to log prob, not, or both.",
    )

    parser.add_argument(
        "--with_few_shot_task_or_format",
        type=str,
        default="format",
        help="Use few-shot samples from the same exact task.",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()
    run_main(args)
