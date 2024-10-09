import numpy as np
from scipy.stats import ttest_ind
import math

from Analysis.diff_of_diff import (
    convert_certainty_full_df_for_stats,
    convert_decoy_full_df_for_stats,
)


def get_decoy_ttest(full_df):
    bias, unbiased = convert_decoy_full_df_for_stats(full_df)

    return ttest_ind(a=bias, b=unbiased, equal_var=True).pvalue


def get_certainty_ttest(full_df):
    bias, unbiased = convert_certainty_full_df_for_stats(full_df)
    return ttest_ind(a=bias, b=unbiased, equal_var=True).pvalue


def get_false_belief_ttest(full_df):
    is_real = full_df["Option"] == "Real-life Objects"
    is_valid = full_df["Valid"] == "Valid"
    is_believable = full_df["Believable"] == "Believable"
    is_undecided = full_df["Percentage"] == -1
    translation_dict = {False: 0, True: 1}

    # first bias
    rvu_bias = full_df[is_real & is_valid & ~is_believable & ~is_undecided][
        "Percentage"
    ]
    nv_unbiased = full_df[~is_real & is_valid & ~is_undecided]["Percentage"]

    rvu_bias = rvu_bias.map(translation_dict)
    nv_unbiased = nv_unbiased.map(translation_dict)
    pvalue_1 = ttest_ind(a=rvu_bias, b=nv_unbiased, equal_var=True).pvalue

    # second bias
    rib_bias = full_df[is_real & ~is_valid & is_believable & ~is_undecided][
        "Percentage"
    ]
    ni_unbiased = full_df[~is_real & ~is_valid & ~is_undecided]["Percentage"]

    rib_bias = rib_bias.map(translation_dict)
    ni_unbiased = ni_unbiased.map(translation_dict)
    pvalue_2 = ttest_ind(a=rib_bias, b=ni_unbiased, equal_var=True).pvalue

    if math.isnan(pvalue_1):
        print("pvalue_1 is None")
        pvalue_1 = 1.0
    if math.isnan(pvalue_2):
        print("pvalue_2 is None")
        pvalue_2 = 1.0

    return round(pvalue_1, 3), round(pvalue_2, 3)


def compute_decoy_bias_scores(pred_df, confidences, full_df):
    no_decoy_target_score = pred_df[pred_df["Type"] == "No Decoy"]["Target"].iloc[0]
    decoy_bias_target_score = pred_df[pred_df["Type"] == "Decoy Worse than Target"][
        "Target"
    ].iloc[0]
    no_decoy_undecided_score = pred_df[pred_df["Type"] == "No Decoy"]["Undecided"].iloc[
        0
    ]
    decoy_bias_undecided_score = pred_df[pred_df["Type"] == "Decoy Worse than Target"][
        "Undecided"
    ].iloc[0]
    diff_score = round(decoy_bias_target_score - no_decoy_target_score, 2)
    undecided_scores = {
        "Undecided Bias Decoy": decoy_bias_undecided_score,
        "Undecided No Decoy": no_decoy_undecided_score,
    }

    target_prob_mean = {
        "Mean Prob Bias Decoy": round(
            confidences[(confidences["Condition"] == "Decoy Worse than Target")][
                "prob_mean"
            ].mean()
            * 100,
            2,
        ),
        "Mean Prob No Decoy": round(
            confidences[(confidences["Condition"] == "No Decoy")]["prob_mean"].mean()
            * 100,
            2,
        ),
    }
    p_value = get_decoy_ttest(full_df)

    return (
        diff_score,
        undecided_scores,
        target_prob_mean,
        p_value,
    )


def compute_certainty_mean_prob_per_choice(confidences):
    choices_prob_mean = {
        "Target mean Prob Treatment": round(
            confidences[
                (confidences["Condition"] == "Target is prize with certainty")
                & (confidences["model_pred"] == "target")
            ]["prob_mean"].mean()
            * 100,
            2,
        ),
        "Target mean Prob Control": round(
            confidences[
                (confidences["Condition"] == "Target is risky too")
                & (confidences["model_pred"] == "target")
            ]["prob_mean"].mean()
            * 100,
            2,
        ),
        "Non-Target mean Prob Treatment": round(
            confidences[
                (confidences["Condition"] == "Target is prize with certainty")
                & (confidences["model_pred"] != "target")
            ]["prob_mean"].mean()
            * 100,
            2,
        ),
        "Non-Target mean Prob Control": round(
            confidences[
                (confidences["Condition"] == "Target is risky too")
                & (confidences["model_pred"] != "target")
            ]["prob_mean"].mean()
            * 100,
            2,
        ),
    }

    return choices_prob_mean


def compute_certainty_bias_scores(pred_df, confidences, full_df):
    no_bias_target_score = pred_df[pred_df["Type"] == "Target is risky too"][
        "Target"
    ].iloc[0]
    certainty_bias_target_score = pred_df[
        pred_df["Type"] == "Target is prize with certainty"
    ]["Target"].iloc[0]
    no_bias_undecided_score = pred_df[pred_df["Type"] == "Target is risky too"][
        "Undecided"
    ].iloc[0]
    certainty_bias_undecided_score = pred_df[
        pred_df["Type"] == "Target is prize with certainty"
    ]["Undecided"].iloc[0]
    diff_score = round(certainty_bias_target_score - no_bias_target_score, 2)
    undecided_scores = {
        "Undecided Treatment Certainty": round(certainty_bias_undecided_score, 2),
        "Undecided Control": round(no_bias_undecided_score, 2),
    }

    choice_prob_mean = compute_certainty_mean_prob_per_choice(confidences)
    p_value = get_certainty_ttest(full_df)

    return (
        diff_score,
        undecided_scores,
        choice_prob_mean,
        p_value,
    )


def update_undecided_scores(undecided_scores, pred_df):
    undecided_scores["Undecided Real-life Objects"] = pred_df[
        pred_df["Type"] == "Undecided"
    ]["Real-life Objects"].iloc[0]
    undecided_scores["Undecided Non-real Objects"] = pred_df[
        pred_df["Type"] == "Undecided"
    ]["Non-real Objects"].iloc[0]


def get_fb_ans_prob_mean(full_df):
    real_life_log_prob_sum = np.logaddexp.reduce(
        full_df[full_df["Option"] == "Real-life Objects"]["log_prob"].to_numpy(
            dtype="float64"
        )
    )
    real_life_log_prob_mean = real_life_log_prob_sum - np.log(
        len(full_df[full_df["Option"] == "Real-life Objects"]["log_prob"])
    )

    non_real_log_prob_sum = np.logaddexp.reduce(
        full_df[full_df["Option"] == "Non-real Objects"]["log_prob"].to_numpy(
            dtype="float64"
        )
    )
    non_real_log_prob_mean = non_real_log_prob_sum - np.log(
        len(full_df[full_df["Option"] == "Non-real Objects"]["log_prob"])
    )

    ans_prob_mean = {
        "Real-life Objects Answer Prob": np.exp(real_life_log_prob_mean) * 100,
        "Non-real Objects Answer Prob": np.exp(non_real_log_prob_mean) * 100,
    }

    return ans_prob_mean


def update_compare_dict_fb_bias_scores(comparing_dict, pred_df):
    if "real_valid_acceptance" not in comparing_dict:
        comparing_dict["real_valid_acceptance"] = []
        comparing_dict["real_invalid_acceptance"] = []
        comparing_dict["non_real_valid_acceptance"] = []
        comparing_dict["non_real_invalid_acceptance"] = []
        comparing_dict["Real Accuracy"] = []
        comparing_dict["Non-Real Accuracy"] = []

    non_real_valid_acceptance = pred_df[
        (pred_df["Type"] == "Valid-Unbelievable")
        | (pred_df["Type"] == "Valid-Believable")
    ]["Non-real Objects"].mean()
    non_real_invalid_acceptance = pred_df[
        (pred_df["Type"] == "Invalid-Unbelievable")
        | (pred_df["Type"] == "Invalid-Believable")
    ]["Non-real Objects"].mean()
    real_valid_acceptance = pred_df[
        (pred_df["Type"] == "Valid-Unbelievable")
        | (pred_df["Type"] == "Valid-Believable")
    ]["Real-life Objects"].mean()
    real_invalid_acceptance = pred_df[
        (pred_df["Type"] == "Invalid-Unbelievable")
        | (pred_df["Type"] == "Invalid-Believable")
    ]["Real-life Objects"].mean()

    comparing_dict["non_real_valid_acceptance"].append(non_real_valid_acceptance)
    comparing_dict["non_real_invalid_acceptance"].append(non_real_invalid_acceptance)

    comparing_dict["real_valid_acceptance"].append(real_valid_acceptance)
    comparing_dict["real_invalid_acceptance"].append(real_invalid_acceptance)
    comparing_dict["Real Accuracy"].append(
        np.mean(
            [
                real_valid_acceptance,
                1 - real_invalid_acceptance,
            ]
        )
    )
    comparing_dict["Non-Real Accuracy"].append(
        np.mean(
            [
                non_real_valid_acceptance,
                1 - non_real_invalid_acceptance,
            ]
        )
    )


def calc_fb_bias_scores_per_score_type(bias_scores, confidences, score_type):
    is_real = confidences["Option"] == "Real-life Objects"
    is_valid = confidences["is_valid"] == True
    is_believable = confidences["is_believable"] == True

    vu_no_bias_target_score = confidences[~is_real & is_valid & ~is_believable][
        score_type
    ].iloc[0]
    vb_no_bias_target_score = confidences[~is_real & is_valid & is_believable][
        score_type
    ].iloc[0]
    valid_no_bias_target_score = (vu_no_bias_target_score + vb_no_bias_target_score) / 2

    iu_no_bias_target_score = confidences[~is_real & ~is_valid & ~is_believable][
        score_type
    ].iloc[0]
    ib_no_bias_target_score = confidences[~is_real & ~is_valid & is_believable][
        score_type
    ].iloc[0]
    invalid_no_bias_target_score = (
        iu_no_bias_target_score + ib_no_bias_target_score
    ) / 2

    vu_bias_target_score = confidences[is_real & is_valid & ~is_believable][
        score_type
    ].iloc[0]
    bias_scores[score_type]["Valid-Unbelievable"] = (
        valid_no_bias_target_score - vu_bias_target_score
    )
    ib_bias_target_score = confidences[is_real & ~is_valid & is_believable][
        score_type
    ].iloc[0]

    bias_scores[score_type]["Invalid-Believable"] = (
        ib_bias_target_score - invalid_no_bias_target_score
    )


def compute_false_belief_bias_scores(pred_df, confidences, full_df, comparing_dict):
    diff_scores = {}
    undecided_scores = {}

    bias_scores = {"low": {}, "mean": {}, "high": {}}
    for score_type in ["mean", "low", "high"]:
        calc_fb_bias_scores_per_score_type(bias_scores, confidences, score_type)

    diff_scores = bias_scores["mean"]

    full_df_without_undecided = full_df[full_df["Percentage"] != -1]

    update_undecided_scores(undecided_scores, pred_df)
    ans_prob_mean = get_fb_ans_prob_mean(full_df_without_undecided)
    update_compare_dict_fb_bias_scores(comparing_dict, pred_df)

    diff_score = [round(v, 2) for v in diff_scores.values()]
    p_value = get_false_belief_ttest(full_df_without_undecided)

    return (
        diff_score,
        undecided_scores,
        ans_prob_mean,
        p_value,
    )


def get_bias_scores(bias_name, pred_df, confidences, full_df, comparing_dict):
    if bias_name == "decoy":
        scores = compute_decoy_bias_scores(pred_df, confidences, full_df)
    elif bias_name == "certainty":
        scores = compute_certainty_bias_scores(pred_df, confidences, full_df)
    elif bias_name == "false_belief":
        scores = compute_false_belief_bias_scores(
            pred_df, confidences, full_df, comparing_dict
        )
    else:
        raise Exception(f"not supported bias name {bias_name}")

    return scores
