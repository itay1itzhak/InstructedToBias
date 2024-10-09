import numpy as np
import pandas as pd
import logging
from scipy.stats import bootstrap


def get_certainty_ans_percentage(all_ans):
    ans_treatment = all_ans["ans_treatment"]
    ans_control = all_ans["ans_control"]

    n_treatment = len(ans_treatment)
    n_control = len(ans_control)

    better_expected_value = [
        ans_treatment.count("better_expected_value") / n_treatment,
        ans_control.count("better_expected_value") / n_control,
    ]
    target = [
        ans_treatment.count("target") / n_treatment,
        ans_control.count("target") / n_control,
    ]

    undecided = [
        ans_treatment.count("-1") / n_treatment,
        ans_control.count("-1") / n_control,
    ]
    return better_expected_value, target, undecided


def get_certainty_results(all_ans):
    better_expected_value, target, undecided = get_certainty_ans_percentage(all_ans)

    full_df = pd.DataFrame.from_dict(
        {
            "Target is prize with certainty": all_ans["ans_treatment"],
            "Probabilities Target is prize with certainty": all_ans["probs_treatment"],
            "Target is risky too": all_ans["ans_control"],
            "Probabilities Target is risky too": all_ans["probs_control"],
        },
        orient="index",
    )
    confidences = get_certainty_bi(full_df)

    df = pd.DataFrame(
        {
            "Type": ["Target is prize with certainty", "Target is risky too"],
            "Higher Expected Value": better_expected_value,
            "Target": target,
            "Undecided": undecided,
        }
    )

    return df, full_df, confidences


def get_certainty_bi(df):
    # calculate 95% bootstrapped confidence interval for mean
    res = []
    row_index = 0
    # for exp_name, row in df.iterrows():
    while row_index < len(df):
        row = df.iloc[row_index]
        probs_row = df.iloc[row_index + 1]
        exp_name = row.name

        for current_option in ["better_expected_value", "target"]:
            option_mean = np.mean(row.dropna() == current_option)
            option_log_prob_sum = np.logaddexp.reduce(
                probs_row.dropna()[row.dropna() == current_option].to_numpy(
                    dtype="float64"
                )
            )
            option_log_prob_mean = option_log_prob_sum - np.log(
                len(probs_row.dropna()[row.dropna() == current_option])
            )

            bootstrap_ci = bootstrap(
                (row.dropna() == current_option,),
                np.mean,
                confidence_level=0.95,
                random_state=1,
                method="percentile",  # "BCa",
                n_resamples=1000,
            ).confidence_interval
            res.append(
                {
                    "Condition": exp_name,
                    "model_pred": current_option,
                    "low": bootstrap_ci.low,
                    "mean": option_mean,
                    "high": bootstrap_ci.high,
                    "prob_mean": np.exp(option_log_prob_mean),
                }
            )
        row_index += 2
    return pd.DataFrame(res)


def analyze_certainty_answer(cur_sample, model_ans, results):
    better_expected_value = cur_sample["metadata"]["better_expected_value"]
    target = cur_sample["metadata"]["target"]

    if model_ans == better_expected_value:
        ans_meaning = "better_expected_value"
    elif model_ans == target:
        ans_meaning = "target"
    else:
        ans_meaning = "-1"
    results["all_ans_meaning"].append(ans_meaning)

    if cur_sample["metadata"]["subtemplates"]["permutation_index"] == 1:
        target_option_location = 2
    else:
        target_option_location = 1
    sample_id = frozenset(
        (
            # "bias_type_index="
            # + str(cur_sample["metadata"]["subtemplates"]["bias_type_index"]),
            # "vals_index=" + str(cur_sample["metadata"]["subtemplates"]["vals_index"]),
            f"target_option_location=" + str(target_option_location),
            "template=" + str(cur_sample["metadata"]["template"]),
            # + str(cur_sample["metadata"]["subtemplates"]["permutation_index"]),
        )
    )

    return sample_id, ans_meaning
