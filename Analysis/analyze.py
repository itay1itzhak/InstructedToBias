import json
import logging
from pathlib import Path
import re

from Analysis.certainty_analysis import analyze_certainty_answer, get_certainty_results
from Analysis.decoy_analysis import analyze_decoy_answer, get_decoy_results
from Analysis.fb_analysis import analyze_false_belief, get_false_belief_results

from utils import (
    FLAN_T5_MODELS,
    OPENAI_MODELS,
    T5_MODELS,
    LLAMA_CHAT_MODELS,
    LLAMA_MODELS,
    get_results_comments_name,
)
from Predict.predict import get_possible_answers
from Data_generation.templates import (
    FB_UNDECIDED_ANSWERS,
    CERTAINTY_TEMPLATES,
)
from Analysis.answers_strings import (
    ANSWERS_TOKENS,
)

logging.basicConfig(level=logging.INFO)


def extract_ans_and_percentage_from_results(results_treatment, results_control):
    all_ans = {
        "ans_treatment": results_treatment["all_ans_meaning"],
        "ans_control": results_control["all_ans_meaning"],
        "probs_treatment": results_treatment["all_model_log_prob_ans"],
        "probs_control": results_control["all_model_log_prob_ans"],
    }

    all_options_percentage = {
        "Treatment Option 1 Percentage": results_treatment["options_percentages"][0],
        "Control Option 1 Percentage": results_control["options_percentages"][0],
        "Treatment Option 2 Percentage": results_treatment["options_percentages"][1],
        "Control Option 2 Percentage": results_control["options_percentages"][1],
        "Treatment Option 3 Percentage": results_treatment["options_percentages"][2],
        "Control Option 3 Percentage": results_control["options_percentages"][2],
    }

    return all_ans, all_options_percentage


def get_all_ans(
    bias_name,
    bias_types,
    engine,
    conditions,
    predict_according_to_log_probs,
    logging_path,
    file_prefix,
    pred_dir,
    is_conditions_are_logical_and_or_logical_or,
):
    with open(logging_path.with_suffix(".txt"), "a+") as f:
        f.write("===Treatment===\n")
    results_treatment = extract_answers_from_predictions(
        f"{file_prefix}_{bias_types}_Treatment_with_metadata.json",
        bias_name,
        engine,
        conditions,
        predict_according_to_log_probs,
        logging_path.with_suffix(".txt"),
        is_conditions_are_logical_and_or_logical_or,
    )

    with open(logging_path.with_suffix(".txt"), "a+") as f:
        f.write("===Control===\n")
    results_control = extract_answers_from_predictions(
        f"{file_prefix}_{bias_types}_Control_with_metadata.json",
        bias_name,
        engine,
        conditions,
        predict_according_to_log_probs,
        logging_path.with_suffix(".txt"),
        is_conditions_are_logical_and_or_logical_or,
    )

    all_ans, all_options_percentage = extract_ans_and_percentage_from_results(
        results_treatment, results_control
    )

    return all_ans, all_options_percentage


def get_all_dfs(bias_name, all_ans, ylabel):
    if bias_name == "decoy":
        results_df, full_df, confidences = get_decoy_results(all_ans)
    elif bias_name == "certainty":
        results_df, full_df, confidences = get_certainty_results(all_ans)
    elif bias_name == "false_belief":
        results_df, full_df, confidences = get_false_belief_results(all_ans, ylabel)
    else:
        raise ValueError(f"bias_name={bias_name} is not supported")

    return results_df, full_df, confidences


def write_results_to_file(
    results_df,
    confidences,
    logging_path,
    file_prefix,
    conditions,
    templates,
    bias_types,
):
    logging.info(results_df)
    res_f_name = file_prefix.with_stem(
        get_results_comments_name(conditions, templates, bias_types)
    ).with_suffix(".csv")
    results_df.to_csv(res_f_name)
    if confidences is not None:
        confidences.to_csv(res_f_name.with_stem(res_f_name.stem + "confidences"))
        with open(logging_path.with_suffix(".txt"), "a+") as f:
            f.write("===Bootstrapping Confidence Intervals===\n")
            f.write(f"{confidences.to_string()}\n")


def get_predictions_analysis(
    bias_name,
    bias_types,
    engine,
    templates,
    conditions={},
    predict_according_to_log_probs=False,
    ylabel="percentage of Choice",
    logging_path=None,
    file_prefix=None,
    pred_dir=None,
    is_conditions_are_logical_and_or_logical_or="logical_and",
):
    all_ans, all_options_percentage = get_all_ans(
        bias_name,
        bias_types,
        engine,
        conditions,
        predict_according_to_log_probs,
        logging_path,
        file_prefix,
        pred_dir,
        is_conditions_are_logical_and_or_logical_or,
    )

    results_df, full_df, confidences = get_all_dfs(bias_name, all_ans, ylabel)

    write_results_to_file(
        results_df,
        confidences,
        logging_path,
        file_prefix,
        conditions,
        templates,
        bias_types,
    )

    return (
        results_df,
        full_df,
        confidences,
        all_options_percentage,
    )


def get_model_ans_according_to_log_probs(all_tokens, all_log_probs, bias_name):
    model_ans = -1
    answer_log_prob = -float("inf")

    pred_ans_line = " ".join(all_tokens).split("\n")[-1]
    all_possible_ans = get_possible_answers(bias_name=bias_name)
    for i, possible_ans in enumerate(all_possible_ans):
        if possible_ans[0] in pred_ans_line or possible_ans[0] in pred_ans_line.replace(
            "  ", " "
        ):
            if bias_name == "decoy" or bias_name == "certainty":
                model_ans = i + 1
            elif bias_name == "false_belief":
                model_ans = True if " valid" in possible_ans[0] else False
            answer_log_prob = all_log_probs[-1]
            break
    return model_ans, answer_log_prob


def check_for_undecided_answer(
    all_tokens, undecided_answers, pred_id, model_ans, answer_log_prob
):
    all_tokens_string = " ".join(all_tokens)
    all_tokens_string_no_spaces = "".join(all_tokens)
    # if "cannot be definitively" in all_tokens_string:
    if any(
        [
            undecided_answer in all_tokens_string
            or undecided_answer in all_tokens_string_no_spaces
            for undecided_answer in undecided_answers
        ]
    ):
        model_ans = -1
        answer_log_prob = -float("inf")
        logging.info(
            f"Model refuse to decide on correct answer on false_belief. pred_id={pred_id}"
        )
        logging.info(all_tokens_string)

    return model_ans, answer_log_prob


def find_ans_in_tokens(bias_name, all_tokens, all_log_probs, valid_options):
    model_ans = -1
    answer_log_prob = -float("inf")

    # remove the explanation part (mainly llama2-chat answers)
    if "Explanation:" in all_tokens:
        all_tokens = all_tokens[: all_tokens.index("Explanation:")]

    # if long answer, reverse it since it's probably an explanation with an answer at the end (mainly GPT4 answers)
    if len(all_tokens) > 100:
        all_tokens = all_tokens[::-1]

    # Select the appropriate options based on bias_name
    valid_options = ANSWERS_TOKENS.get(bias_name, {})

    # Find the answer in the tokens
    for i, token in enumerate(all_tokens):
        token = token.strip()
        # if token is a valid option
        if token in valid_options:
            model_ans = valid_options[token]
            answer_log_prob = all_log_probs[i]
            break

    return model_ans, answer_log_prob


def get_model_ans(
    pred_id,
    all_tokens,
    all_log_probs,
    predict_according_to_log_probs,
    bias_name,
):
    if predict_according_to_log_probs:  # the answser is one of the options
        return get_model_ans_according_to_log_probs(
            all_tokens, all_log_probs, bias_name
        )

    model_ans, answer_log_prob = find_ans_in_tokens(
        bias_name, all_tokens, all_log_probs, valid_options=ANSWERS_TOKENS
    )

    # check if the answer is an undecided answer
    if bias_name == "false_belief":
        model_ans, answer_log_prob = check_for_undecided_answer(
            all_tokens, FB_UNDECIDED_ANSWERS, pred_id, model_ans, answer_log_prob
        )

    if bias_name == "certainty":
        model_ans, answer_log_prob = check_for_undecided_answer(
            all_tokens,
            CERTAINTY_TEMPLATES["CERTAINTY_UNDECIDED_ANSWERS"],
            pred_id,
            model_ans,
            answer_log_prob,
        )

    return model_ans, answer_log_prob


def move_values_to_metadata(cur_sample):
    for attribute, value in cur_sample["metadata"]["subtemplates"].items():
        cur_sample["metadata"][attribute] = value
    inner_attributes = {}
    for outer_attribute, value in cur_sample["metadata"].items():
        cur_outer = cur_sample["metadata"][outer_attribute]
        if type(cur_outer) == type({}):
            for inner_attribute, inner_value in cur_outer.items():
                inner_attributes[outer_attribute + ">" + inner_attribute] = inner_value
    for inner_attribute, inner_value in inner_attributes.items():
        cur_sample["metadata"][inner_attribute] = inner_value


def is_attribute_in_cur_samples(cur_sample, attribute, value):
    values_list = value.split(",")
    numerical_values_list = []
    try:
        for v in values_list:
            numerical_values_list.append(int(v))
    except Exception as e:
        pass
    return (
        attribute not in cur_sample["metadata"]
        or cur_sample["metadata"][attribute] in values_list
        or str(cur_sample["metadata"][attribute]) in values_list
        or cur_sample["metadata"][attribute] in numerical_values_list
    )


def should_skip_cur_sample(
    cur_sample, conditions, is_conditions_are_logical_and_or_logical_or
):
    should_skip_sample = True
    cur_sample = cur_sample.copy()
    # for certainty
    if cur_sample["metadata"]["bias_name"] == "certainty":
        move_values_to_metadata(cur_sample)

    for and_condition in conditions:
        should_skip_sample = False
        for attribute, value in and_condition.items():
            if is_attribute_in_cur_samples(cur_sample, attribute, value):
                should_skip_sample = False
                if is_conditions_are_logical_and_or_logical_or == "logical_or":
                    break  # [Or] if one of the conditions is met, don't skip the sample
            else:
                should_skip_sample = True
                if is_conditions_are_logical_and_or_logical_or == "logical_and":
                    break  # [And] if one of the conditions is not met, skip the sample
        if not should_skip_sample:
            break
    return should_skip_sample


def update_results_with_cur_pred(results, cur_pred, model_ans, answer_log_prob):
    results["human_or_right_answer"].append(
        cur_pred["metadata"]["human_or_right_answer"]
    )
    results["bias_type"].append(cur_pred["metadata"]["bias_type"])
    results["all_model_ans"].append(model_ans)
    results["all_model_log_prob_ans"].append(answer_log_prob)


def add_check_agreement(
    sample_id,
    ans_meaning,
    already_seen_samples_ids: dict,
    results: dict,
):
    # if we have not seen this sample before, add it to the dict
    if sample_id not in already_seen_samples_ids:
        already_seen_samples_ids[sample_id] = ans_meaning
        results["agreements_between_permutations"][sample_id] = [ans_meaning]
    # if we have seen this sample before, add it to the dict of similar samples
    else:
        results["agreements_between_permutations"][sample_id].append(ans_meaning)


def analyze_answer_from_sample_prediction(
    pred_id: int,
    model_ans: int,
    answer_log_prob: float,
    human_or_right_answer: str,
    bias_name: str,
    preds_json: dict,
    conditions: dict,
    results: dict,
    already_seen_samples_ids: dict,
    is_conditions_are_logical_and_or_logical_or: str,
):
    cur_pred = preds_json[pred_id]

    # check if should skip sample according to conditions if they exist
    if conditions != {}:
        if should_skip_cur_sample(
            cur_pred, conditions, is_conditions_are_logical_and_or_logical_or
        ):
            return

    update_results_with_cur_pred(results, cur_pred, model_ans, answer_log_prob)

    if bias_name == "decoy":
        sample_id, ans_meaning = analyze_decoy_answer(cur_pred, model_ans, results)
    elif bias_name == "certainty":
        sample_id, ans_meaning = analyze_certainty_answer(
            cur_pred,
            model_ans,
            results,
        )
    elif bias_name == "false_belief":
        sample_id, ans_meaning = analyze_false_belief(
            cur_pred,
            model_ans,
            results,
        )

    add_check_agreement(sample_id, ans_meaning, already_seen_samples_ids, results)


def write_agreement_percent(results: dict, logging_path: Path):
    text_to_output = ""
    all_unique_groups = results[
        "agreements_between_permutations"
    ]  # list(results["agreements_between_permutations"].values())
    mean_group_percent_agree = 0

    for group_id, all_pred_in_group in all_unique_groups.items():
        # count how many predictions inside a group are the same
        group_count_agree = sum(
            pred == all_pred_in_group[0] for pred in all_pred_in_group
        )
        mean_group_percent_agree += group_count_agree / len(all_pred_in_group)

    text_to_output += f"Number of groups - {len(all_unique_groups)}\n"
    text_to_output += f"Mean percentage of elements that have agreement within each group - {mean_group_percent_agree/len(all_unique_groups):.2%}\n"

    logging.info(text_to_output)
    with open(logging_path.with_suffix(".txt"), "a+") as f:
        f.write(text_to_output)


def write_each_group_success_percent(bias_name: str, results: dict, logging_path: Path):
    text_to_output = ""
    all_unique_groups = list(results["agreements_between_permutations"].values())

    if bias_name == "false_belief":
        for i, group_vals in enumerate(all_unique_groups):
            count_correct = 0
            for v in group_vals:
                if v["model_pred_is_valid"] == v["is_valid"]:
                    count_correct += 1

            text_to_output += f"Percentage of correct answers in group {i} - {count_correct/len(group_vals):.2%}\n"
    # for decoy and certainty
    else:
        for g, v in results["agreements_between_permutations"].items():
            g_target = v.count("target") / len(v)
            text_to_output += f"Percentage of model answers which is Target in agreement group {g} - {g_target:.2%}\n"

    logging.info(text_to_output)
    with open(logging_path.with_suffix(".txt"), "a+") as f:
        f.write(text_to_output)


def calc_options_percentages(bias_name, results, logging_path):
    opt1_count = results["all_model_ans"].count(1) / len(results["all_model_ans"])
    opt2_count = results["all_model_ans"].count(2) / len(results["all_model_ans"])
    opt3_count = results["all_model_ans"].count(3) / len(results["all_model_ans"])
    if bias_name == "false_belief":
        opt1_count = results["all_model_ans"].count(0) / len(results["all_model_ans"])
        opt2_count = results["all_model_ans"].count(1) / len(results["all_model_ans"])
    no_opt_count = results["all_model_ans"].count(-1) / len(results["all_model_ans"])
    results["options_percentages"] = [
        round(opt1_count, 2),
        round(opt2_count, 2),
        round(opt3_count, 2),
        round(no_opt_count, 2),
    ]

    human_or_right_answer_opt1_count = results["human_or_right_answer"].count(1) / len(
        results["human_or_right_answer"]
    )
    human_or_right_answer_opt2_count = results["human_or_right_answer"].count(2) / len(
        results["human_or_right_answer"]
    )
    human_or_right_answer_opt3_count = results["human_or_right_answer"].count(3) / len(
        results["human_or_right_answer"]
    )
    if bias_name == "false_belief":
        human_or_right_answer_opt1_count = results["human_or_right_answer"].count(
            0
        ) / len(results["human_or_right_answer"])
    human_or_right_answer_opt2_count = results["human_or_right_answer"].count(1) / len(
        results["human_or_right_answer"]
    )

    results["human_or_right_answer_options_percentages"] = [
        human_or_right_answer_opt1_count,
        human_or_right_answer_opt2_count,
        human_or_right_answer_opt3_count,
    ]

    output_text = "\n".join(
        [
            f"Percentage in data of Option 1 - {human_or_right_answer_opt1_count:.2%}",
            f"Percentage in data of Option 2 - {human_or_right_answer_opt2_count:.2%}",
            f"Percentage in data of Option 3 - {human_or_right_answer_opt3_count:.2%}",
            f"Percentage of Option 1 - {opt1_count:.2%}",
            f"Percentage of Option 2 - {opt2_count:.2%}",
            f"Percentage of Option 3 - {opt3_count:.2%}",
            f"Percentage of Undecided answers - {no_opt_count:.2%}",
            "-" * 50,
        ]
    )

    logging.info(output_text)

    with open(logging_path.with_suffix(".txt"), "a+") as f:
        f.write(output_text)


def load_predictions(predictions_path, bias_name, conditions):
    try:
        with open(predictions_path) as f_pred:
            preds_json = json.load(f_pred)
    except Exception as e:
        logging.info(
            f"Could not load json!\npredictions_path={predictions_path}\nbias_name={bias_name}\nconditions={conditions}"
        )
        raise e

    logging.info(f"Extracting {len(preds_json)} Answers from file:{predictions_path}")

    return preds_json


def preprocess_predictions(prediction, engine):
    all_tokens = re.split(" |\n|,|\.", prediction["prediction"])
    if engine in OPENAI_MODELS and not engine == "gpt-4-0314":
        all_tokens = prediction["metadata"]["logprobs"]["tokens"]
        all_log_probs = prediction["metadata"]["logprobs"]["token_logprobs"]
    elif engine == "gpt-4-0314":
        all_log_probs = [-10000] * len(all_tokens)  # no logprobs for this model
    elif engine in FLAN_T5_MODELS:
        all_log_probs = list(prediction["metadata"]["log_probs"].values())
    elif engine in T5_MODELS:
        all_log_probs = [prediction["metadata"]["log_probs"]]
    elif engine in LLAMA_CHAT_MODELS:
        # all_tokens = [t[0] for t in prediction["metadata"]["log_probs"]]
        all_log_probs = [t[1] for t in prediction["metadata"]["log_probs"]]
    elif engine in LLAMA_MODELS:
        all_log_probs = [prediction["metadata"]["log_probs"]]
    else:
        raise ValueError(f"Cannot find tokens or logprobs for {engine =}")

    return all_tokens, all_log_probs


def extract_answers_from_predictions(
    predictions_path: str,
    bias_name: str,
    engine: str,
    conditions: dict,
    predict_according_to_log_probs: bool,
    logging_path: str,
    is_conditions_are_logical_and_or_logical_or: str,
):
    results = {
        "all_model_ans": [],
        "all_model_log_prob_ans": [],
        "all_expected_ans": [],
        "all_ans_meaning": [],
        "human_or_right_answer": [],
        "agreements_between_permutations": dict(),
        "price_target": [],
        "price_competitor": [],
        "bias_type": [],
    }

    preds_json = load_predictions(predictions_path, bias_name, conditions)
    already_seen_samples_ids = dict()
    for pred_id in preds_json:
        prediction = preds_json[pred_id]
        all_tokens, all_log_probs = preprocess_predictions(prediction, engine)

        model_ans, answer_log_prob = get_model_ans(
            pred_id,
            all_tokens,
            all_log_probs,
            predict_according_to_log_probs,
            bias_name,
        )

        human_or_right_answer = prediction["metadata"]["human_or_right_answer"]
        analyze_answer_from_sample_prediction(
            pred_id,
            model_ans,
            answer_log_prob,
            human_or_right_answer,
            bias_name,
            preds_json,
            conditions,
            results,
            already_seen_samples_ids,
            is_conditions_are_logical_and_or_logical_or,
        )

    assert (
        len(results["all_model_ans"])
        == len(results["all_model_log_prob_ans"])
        == len(results["all_ans_meaning"])
    )
    calc_options_percentages(bias_name, results, logging_path)
    write_agreement_percent(results, logging_path)
    write_each_group_success_percent(bias_name, results, logging_path)

    return results
