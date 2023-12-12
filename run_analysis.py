from Analysis.analyze import (
    get_predictions_analysis,
    get_results_comments_name,
)
from Analysis.compute_bias_scores import (
    get_bias_scores,
)
from utils import (
    get_across_exp_result_file_prefix,
    get_bias_type_templates_defaults,
)
from Data_generation.templates import (
    ALL_EXPENSIVE_DECOY_PRODUCTS,
    ALL_CHEAP_DECOY_PRODUCTS,
)
from Analysis.plotting import plot_false_belief, save_plot_hist
from Analysis.diff_of_diff import get_diff_of_diff
from utils import INSTURCT_MODELS

import pandas as pd
import argparse
import logging
from pathlib import Path

from itertools import combinations


logger = logging.getLogger("Ananlysis")
logger.setLevel(logging.INFO)


def get_boolean_vals_from_str(str):
    return [k == "True" for k in str.split(",")]


def get_decoy_default_values(all_products, bias_name):
    if bias_name == "decoy_expensive":
        all_products = ALL_EXPENSIVE_DECOY_PRODUCTS
    elif bias_name == "decoy_cheaper":
        all_products = ALL_CHEAP_DECOY_PRODUCTS
    else:
        raise ValueError(
            f"bias_name={bias_name} is not supported, only decoy_expensive and decoy_cheap or decoy with specific products"
        )
    return all_products


def parse_args(args):
    bias_types = args.bias_type
    if args.bias_name.startswith("decoy"):
        if args.all_products is None:
            all_products = get_decoy_default_values(args.all_products, args.bias_name)
        else:
            all_products = args.all_products.split(",")
    else:
        all_products = [""]

    bias_name = args.bias_name.replace("_expensive", "").replace("_cheaper", "")
    templates = args.templates

    all_k_shot_vanilla = [int(k) for k in args.all_k_shot_vanilla.split(",")]
    all_k_shot_instruct = [int(k) for k in args.all_k_shot_instruct.split(",")]
    all_should_normalize_vanilla = get_boolean_vals_from_str(
        args.all_should_normalize_vanilla
    )
    predict_instruct_according_to_log_probs = (
        args.predict_instruct_according_to_log_probs
    )

    all_should_normalize_instruct = get_boolean_vals_from_str(
        args.all_should_normalize_instruct
    )

    with_task_few_shot = args.with_task_few_shot
    with_format_few_shot = args.with_format_few_shot

    all_models = args.all_models.split(",")
    all_options_permutations = get_boolean_vals_from_str(args.all_options_permutations)

    return (
        bias_name,
        bias_types,
        all_products,
        templates,
        all_k_shot_vanilla,
        all_k_shot_instruct,
        all_should_normalize_vanilla,
        predict_instruct_according_to_log_probs,
        all_should_normalize_instruct,
        with_task_few_shot,
        with_format_few_shot,
        all_models,
        all_options_permutations,
    )


def parse_conditions(args_all_conditions):
    parsed_all_conditions = [{}]
    if args_all_conditions is not None:
        parsed_all_conditions = []
        for joint_condidtions in args_all_conditions.split("*"):
            all_joint_conditions = []
            for cond_ands in joint_condidtions.split("#"):
                and_cond = {}
                for cond in cond_ands.split("&"):
                    k, v = cond.split(":")
                    if k not in and_cond:
                        and_cond[k] = v
                    else:
                        and_cond[k] += "," + v
                all_joint_conditions.append(and_cond)
            parsed_all_conditions.append(all_joint_conditions)

    return parsed_all_conditions


def get_default_across_exp_results_values(bias_name, all_products):
    if bias_name == "decoy":
        values_list = ["Competitor", "Target", "Decoy"]
        ylabel = "Accuracy"
        plot_ylabel = "Percentage Of Choices"
    elif bias_name == "certainty":
        all_products = [""]
        values_list = ["Higher Expected Value", "Target"]
        ylabel = "Accuracy"
        plot_ylabel = "Percentage Of Choices"
    elif bias_name == "false_belief":
        all_products = [""]
        values_list = ["Real-life Objects", "Non-real Objects"]
        ylabel = "acceptance Rate"
        plot_ylabel = ylabel

    return values_list, ylabel, plot_ylabel, all_products


def set_run_args(args):
    (
        bias_name,
        bias_types,
        all_products,
        templates,
        all_k_shot_vanilla,
        all_k_shot_instruct,
        all_should_normalize_vanilla,
        predict_instruct_according_to_log_probs,
        all_should_normalize_instruct,
        with_task_few_shot,
        with_format_few_shot,
        all_models,
        all_options_permutations,
    ) = parse_args(args)

    all_conditions = parse_conditions(args.all_conditions)

    (
        values_list,
        ylabel,
        plot_ylabel,
        all_products,
    ) = get_default_across_exp_results_values(bias_name, all_products)

    bias_types, templates = get_bias_type_templates_defaults(
        bias_name, bias_types, templates
    )

    cross_experiment_settings = {
        "all_models": all_models,
        "all_products": all_products,
        "all_k_shot_instruct": all_k_shot_instruct,
        "all_k_shot_vanilla": all_k_shot_vanilla,
        "all_should_normalize_vanilla": all_should_normalize_vanilla,
        "predict_instruct_according_to_log_probs": predict_instruct_according_to_log_probs,
        "all_should_normalize_instruct": all_should_normalize_instruct,
        "all_options_permutations": all_options_permutations,
        "all_conditions": all_conditions,
        "with_task_few_shot": with_task_few_shot,
        "with_format_few_shot": with_format_few_shot,
    }

    experiment_args = {
        "pred_dir": Path("Predictions/"),
        "values": "generate_values",
        "bias_name": bias_name,
        "bias_types": bias_types,
        "templates": templates,
        "values_list": values_list,
        "ylabel": ylabel,
        "plot_ylabel": plot_ylabel,
        "is_conditions_are_logical_and_or_logical_or": args.is_conditions_are_logical_and_or_logical_or,
    }

    return (experiment_args, cross_experiment_settings)


def unpack_dict_to_dict(dest_dict: dict, org_dict: dict):
    for k, v in org_dict.items():
        if k not in dest_dict:
            dest_dict[k] = []
        dest_dict[k].append(v)


def calc_scores(
    pred_df: pd.DataFrame,
    bias_name: str,
    comparing_dict: dict,
    confidences: pd.DataFrame,
    full_df: pd.DataFrame,
    all_options_percentage: dict,
):
    (
        diff_score,
        undecided_scores,
        target_prob_mean,
        p_value,
    ) = get_bias_scores(bias_name, pred_df, confidences, full_df, comparing_dict)

    comparing_dict["bias_score"].append(diff_score)
    comparing_dict["p_value"].append(p_value)

    unpack_dict_to_dict(comparing_dict, undecided_scores)
    unpack_dict_to_dict(comparing_dict, target_prob_mean)
    unpack_dict_to_dict(comparing_dict, all_options_percentage)


def write_diff_of_diff_report(bias_name, all_dfs, logging_path):
    """gets a list of dicts with keys that are expiremnt names and values are full results df
    and writes a report with the diff of diff results
    """
    diff_of_diff_report = Path(f"{logging_path}_diff_of_diff_report").with_suffix(
        ".csv"
    )
    # create dict to hold the results
    diff_of_diff_results = {}

    all_models_pairs = list(combinations(all_dfs, 2))
    for model_pair in all_models_pairs:
        full_name_first_model = list(model_pair[0].keys())[0]
        full_name_second_model = list(model_pair[1].keys())[0]
        first_model_name = full_name_first_model.split(" | ")[0]
        second_model_name = full_name_second_model.split(" | ")[0]

        experiment_details = full_name_first_model.split(" | ")[1:]
        reg_summery = get_diff_of_diff(
            bias_name,
            model_pair[0][full_name_first_model],
            model_pair[1][full_name_second_model],
        )
        # diff_of_diff_results[f"{first_model_name} VS {second_model_name}"] = [
        diff_of_diff_results[f"{full_name_first_model} VS {full_name_second_model}"] = [
            reg_summery,
            experiment_details,
        ]

    # change results dict to df and save as csv
    diff_of_diff_results_df = pd.DataFrame.from_dict(
        diff_of_diff_results, orient="index", columns=["p-value", "experiment_details"]
    )
    diff_of_diff_results_df.to_csv(diff_of_diff_report)


def update_comparing_dict(comparing_dict, exp_args, full_df):
    comparing_dict = exp_args["comparing_dict"]
    experiment_name = exp_args["experiment_name"]
    comparing_dict["experiment_name"].append(experiment_name)
    # appending full_df with name of the experiment for diff of diff
    comparing_dict["full_df"].append({experiment_name: full_df})


def analyze_experiment(exp_args):
    args_base = [
        "bias_name",
        "engine",
        "predict_according_to_log_probs",
        "templates",
    ]
    args_get_across_exp_result_file_prefix = [
        "pred_dir",
        "product",
        "all_options_permutations",
        "normalize_log_prob",
        "with_format_few_shot",
        "with_task_few_shot",
        "k_shot",
    ]

    file_prefix = get_across_exp_result_file_prefix(
        **{key: exp_args[key] for key in args_base},
        **{key: exp_args[key] for key in args_get_across_exp_result_file_prefix},
    )

    args_get_predictions_analysis = [
        "bias_types",
        "conditions",
        "load_df",
        "ylabel",
        "logging_path",
        "is_conditions_are_logical_and_or_logical_or",
        *{key: exp_args[key] for key in args_base},
    ]

    pred_df, full_df, confidences, all_options_percentage = get_predictions_analysis(
        **{k: v for k, v in exp_args.items() if k in args_get_predictions_analysis},
        file_prefix=file_prefix,
    )

    update_comparing_dict(exp_args["comparing_dict"], exp_args, full_df)

    calc_scores(
        pred_df=pred_df,
        bias_name=exp_args["bias_name"],
        comparing_dict=exp_args["comparing_dict"],
        confidences=confidences,
        full_df=full_df,
        all_options_percentage=all_options_percentage,
    )

    save_plot_hist(
        full_df,
        confidences,
        exp_args["bias_name"],
        exp_args["values_list"],
        model=exp_args["engine"],
        fig_f_name=file_prefix.with_stem(
            file_prefix.stem + exp_args["comments_results_name"]
        ).with_suffix(".pdf"),
        plot_ylabel=exp_args["plot_ylabel"],
    )


def set_experiment(
    experiment_args,
    engine,
    k_shot,
    with_format_few_shot,
    with_task_few_shot,
    predict_according_to_log_probs,
    should_normalize,
    permute,
):
    experiment_args["engine"] = engine
    experiment_args["comparing_dict"]["model"].append(engine)
    experiment_args["comparing_dict"]["k_shot"].append(k_shot)
    experiment_args["comparing_dict"]["normalize"].append(should_normalize)
    experiment_args["all_options_permutations"] = permute
    experiment_args["experiment_name"] = (
        f"{engine} | {k_shot =} | " + experiment_args["product"]
    )
    logging.info(experiment_args["experiment_name"] + "\n")
    logging.info(f"=" * 80)
    with open(experiment_args["logging_path"].with_suffix(".txt"), "a+") as f:
        f.write(f"=" * 80 + "\n")
        f.write(
            experiment_args["experiment_name"]
            + experiment_args["comments_results_name"]
            + "\n"
        )
        f.write(f"=" * 80 + "\n")

    experiment_args["with_format_few_shot"] = with_format_few_shot and k_shot != 0
    experiment_args["with_task_few_shot"] = with_task_few_shot and k_shot != 0
    experiment_args["normalize_log_prob"] = should_normalize
    experiment_args["k_shot"] = k_shot

    experiment_args["predict_according_to_log_probs"] = predict_according_to_log_probs

    return experiment_args


def update_experiment_args(
    experiment_args, conditions, with_format_few_shot, with_task_few_shot
):
    experiment_args["conditions"] = conditions

    log_dir = experiment_args["pred_dir"].joinpath(
        experiment_args["bias_name"],
        experiment_args["product"],
    )
    experiment_args["log_dir"] = log_dir

    experiment_args["comments_results_name"] = get_results_comments_name(
        conditions,
        experiment_args["templates"],
        experiment_args["bias_types"],
    )

    logging_path = Path(
        log_dir,
        f"logging_aux"
        + experiment_args["comments_results_name"]
        + "format_"
        + str(with_format_few_shot)
        + "_task_"
        + str(with_task_few_shot),
    )
    open(logging_path.with_suffix(".txt"), "w+").close()
    experiment_args["logging_path"] = logging_path
    experiment_args["comparing_dict"] = {
        "experiment_name": [],
        "model": [],
        "k_shot": [],
        "normalize": [],
        "bias_score": [],
        "p_value": [],
        "full_df": [],
    }

    return experiment_args


def split_false_belief_bias_scores(comparing_dict):
    comparing_dict[["Belief Valid", "Belief Invalid"]] = (
        comparing_dict["bias_score"]
        .astype(str)
        .str.strip("[]")
        .str.split(",", expand=True)
        .astype(float)
    )


def create_run_report_and_plot(experiment_args, all_models):
    write_diff_of_diff_report(
        experiment_args["bias_name"],
        experiment_args["comparing_dict"]["full_df"],
        experiment_args["logging_path"],
    )
    comparing_dict = pd.DataFrame(experiment_args["comparing_dict"])
    if experiment_args["bias_name"] == "false_belief":
        split_false_belief_bias_scores(comparing_dict)
        plot_false_belief(comparing_dict, experiment_args, all_models)

    # save final results from comparing_dict as csv
    comparing_dict.to_csv(
        experiment_args["logging_path"].with_suffix(".csv"), float_format="%.3f"
    )


def across_products_diff_of_diff(
    all_full_df_for_significance, logging_path, all_products
):
    """
    gets a list of full_df for all products. The function unify the products per model and run write_diff_of_diff_report
    """
    unified_full_dfs = []
    for i, product_exp_list in enumerate(all_full_df_for_significance):
        # convert list of dicts (model->df) to a df

        # add every model to unified_full_dfs
        for j, exp_dict in enumerate(product_exp_list):
            exp_name = list(exp_dict.keys())[0]  # get the only key in the dict
            model_name = " | ".join(
                exp_name.split(" | ")[0:2]
            )  # model name without product
            # if model_name not in unified_full_dfs, add it as a new dataframe
            if i == 0:  # this is for the first product
                unified_full_dfs.append(
                    {model_name: exp_dict[exp_name][["Condition", "Choice"]]}
                )  # to fit format for write_diff_of_diff_report
            # else, concat the df to the existing one
            else:
                unified_full_dfs[j][model_name] = pd.concat(
                    [
                        unified_full_dfs[j][model_name],
                        exp_dict[exp_name][["Condition", "Choice"]],
                    ]
                )

    write_diff_of_diff_report(
        "decoy",
        unified_full_dfs,
        logging_path.parent.parent.joinpath(
            f"logging_aux_{str(all_products)}"
        ),  # to save in decoy folder
    )


def set_instructed_args(engine, cross_experiment_settings):
    """
    select the k_shot, should_normalize and predict_according_to_log_probs according to the engine being an instruct model or not
    """
    if engine in INSTURCT_MODELS:
        all_k_shot = cross_experiment_settings["all_k_shot_instruct"]
        predict_according_to_log_probs = cross_experiment_settings[
            "predict_instruct_according_to_log_probs"
        ]
        all_should_normalize = cross_experiment_settings[
            "all_should_normalize_instruct"
        ]
    else:
        all_k_shot = cross_experiment_settings["all_k_shot_vanilla"]
        all_should_normalize = cross_experiment_settings["all_should_normalize_vanilla"]
        predict_according_to_log_probs = True
    return all_k_shot, all_should_normalize, predict_according_to_log_probs


def run_experiments_analysis(
    all_k_shot,
    all_should_normalize,
    predict_according_to_log_probs,
    engine,
    permute,
    conditions,
    experiment_args,
    cross_experiment_settings,
):
    all_failures = []
    for k_shot in all_k_shot:
        for should_normalize in all_should_normalize:
            try:
                experiment_args = set_experiment(
                    experiment_args,
                    engine,
                    k_shot,
                    cross_experiment_settings["with_format_few_shot"],
                    cross_experiment_settings["with_task_few_shot"],
                    predict_according_to_log_probs,
                    should_normalize,
                    permute,
                )
                analyze_experiment(experiment_args)
            except Exception as e:
                print(e)
                experiment_args["comparing_dict"]["model"].pop(-1)
                experiment_args["comparing_dict"]["k_shot"].pop(-1)
                experiment_args["comparing_dict"]["normalize"].pop(-1)
                all_failures.append(
                    f"{experiment_args['product']=},{engine=},{k_shot=},{should_normalize=},{conditions=}"
                )
                raise e
    return all_failures


def run_conditions(experiment_args, cross_experiment_settings):
    all_failures = []
    all_full_df_for_significance = []

    for product in cross_experiment_settings["all_products"]:
        experiment_args["product"] = product
        for conditions in cross_experiment_settings["all_conditions"]:
            experiment_args = update_experiment_args(
                experiment_args,
                conditions,
                cross_experiment_settings["with_format_few_shot"],
                cross_experiment_settings["with_task_few_shot"],
            )
            for engine in cross_experiment_settings["all_models"]:
                (
                    all_k_shot,
                    all_should_normalize,
                    predict_according_to_log_probs,
                ) = set_instructed_args(engine, cross_experiment_settings)
                failures_for_perms = []
                for permute in cross_experiment_settings["all_options_permutations"]:
                    failures_for_perm = run_experiments_analysis(
                        all_k_shot,
                        all_should_normalize,
                        predict_according_to_log_probs,
                        engine,
                        permute,
                        conditions,
                        experiment_args,
                        cross_experiment_settings,
                    )
                    failures_for_perms += failures_for_perm
                all_failures += failures_for_perms

                create_run_report_and_plot(
                    experiment_args,
                    cross_experiment_settings["all_models"],
                )
            all_full_df_for_significance.append(
                experiment_args["comparing_dict"]["full_df"]
            )

    return all_failures, all_full_df_for_significance


def create_all_results_files(args):
    (experiment_args, cross_experiment_settings) = set_run_args(args)

    # run all experiments analysis and save results
    all_failures, all_full_df_for_significance = run_conditions(
        experiment_args, cross_experiment_settings
    )

    # run diff of diff for decoy bias across products
    if experiment_args["bias_name"] == "decoy":
        across_products_diff_of_diff(
            all_full_df_for_significance,
            experiment_args["logging_path"],
            cross_experiment_settings["all_products"],
        )

    # print all runs that failed
    report_failures(all_failures)


def report_failures(all_failures):
    for f in all_failures:
        print(f)
    print(f"Number of all_failures={len(all_failures)}")


def run_main(args):
    create_all_results_files(args)
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
        "--bias_type",
        type=str,
        default=None,
        help="Which bias type to use.",
    )
    parser.add_argument(
        "--engine",
        type=str,
        default="text-davinci-002",
        help="Which model to use.",
    )
    parser.add_argument(
        "--all_models",
        type=str,
        default=None,
        help="Which models to use.",
    )
    parser.add_argument(
        "--all_products",
        type=str,
        default=None,
        help="Which products to analize in decoy bias. Default is all products",
    )
    parser.add_argument(
        "--templates",
        type=str,
        default=None,
        help="Which text templates to analyze in decoy bias.",
    )
    parser.add_argument(
        "--all_conditions",
        type=str,
        default=None,
        help="Which conditions to analize in all biases, such as biast types, specific values templates etc.",
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
        help="If set to true, The prediction of instructions models will be done not by letting the model compelet the prompt, but to measure the probablity log-likelihood of each possible answer.",
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
        "--is_conditions_are_logical_and_or_logical_or",
        type=str,
        default="logical_and",
        help="Are the all the conditions should be met set to logical_and, if only one of the condition is enough set to logical_or. Default is logical_and",
    )

    parser.add_argument(
        "--predict_instruct_according_to_log_probs",
        type=str,
        default=False,
        help="Should instruction models answer according to log prob, not, or both.",
    )

    parser.add_argument(
        "--all_should_normalize_instruct",
        type=str,
        default="False",
        help="Should normlize insturct models answers according to log prob, not, or both.",
    )
    parser.add_argument(
        "--all_options_permutations",
        type=str,
        default="True",
        help="Should analyze all permutations of the options.",
    )

    parser.add_argument(
        "--bias_types",
        type=str,
        default=None,
        help="The bias type in the predicted file name.",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()
    run_main(args)
