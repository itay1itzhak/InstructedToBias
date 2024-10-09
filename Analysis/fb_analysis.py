import pandas as pd
from scipy.stats import bootstrap
import numpy as np
from Data_generation.templates import FB_MORE_THAN_ONE_TOKEN_ANSWERS


def check_for_more_than_one_token_answer(
    all_tokens, answer_log_prob, model_ans, all_log_probs
):
    all_tokens_string = " ".join(all_tokens)

    # if more than one answer is in all_tokens_string:
    for few_tokens_answer, answer_value in FB_MORE_THAN_ONE_TOKEN_ANSWERS.items():
        if few_tokens_answer in all_tokens_string:
            model_ans = answer_value
            answer_log_prob = get_log_prob_of_fb_long_answer(
                few_tokens_answer, all_tokens, all_log_probs
            )

    return model_ans, answer_log_prob


def get_log_prob_of_fb_long_answer(few_tokens_answer, all_tokens, all_log_probs):
    # take the log prob of the last token in the answer (arbitrary choice)
    index_of_few_tokens_answer = all_tokens.index(few_tokens_answer.split(" ")[-1])
    answer_log_prob = all_log_probs[index_of_few_tokens_answer]
    return answer_log_prob


def get_fb_acceptance_percentages(ans_meaning, ans_probs):
    df = pd.DataFrame(ans_meaning)
    # new, not tested!
    df = pd.concat([df, pd.DataFrame(ans_probs)], axis=1)

    # remove samples with undecided answer for confidence calculation
    # confidences = get_fb_bi(df)
    confidences = get_fb_bi(df[df["model_pred_is_valid"] != -1])

    vb_valid = len(
        df[
            (df["model_pred_is_valid"] == True)
            & (df["is_valid"] == True)
            & (df["is_believable"] == True)
        ]
    )
    vb = len(df[(df["is_valid"] == True) & (df["is_believable"] == True)])
    # vb = len(
    #     df[
    #         (df["is_valid"] == True)
    #         & (df["is_believable"] == True)
    #         & (df["model_pred_is_valid"] != -1)
    #     ]
    # )

    vu_valid = len(
        df[
            (df["model_pred_is_valid"] == True)
            & (df["is_valid"] == True)
            & (df["is_believable"] == False)
        ]
    )
    vu = len(df[(df["is_valid"] == True) & (df["is_believable"] == False)])
    # vu = len(
    #     df[
    #         (df["is_valid"] == True)
    #         & (df["is_believable"] == False)
    #         & (df["model_pred_is_valid"] != -1)
    #     ]
    # )

    ib_valid = len(
        df[
            (df["model_pred_is_valid"] == True)
            & (df["is_valid"] == False)
            & (df["is_believable"] == True)
        ]
    )
    ib = len(df[(df["is_valid"] == False) & (df["is_believable"] == True)])
    # ib = len(
    #     df[
    #         (df["is_valid"] == False)
    #         & (df["is_believable"] == True)
    #         & (df["model_pred_is_valid"] != -1)
    #     ]
    # )

    iu_valid = len(
        df[
            (df["model_pred_is_valid"] == True)
            & (df["is_valid"] == False)
            & (df["is_believable"] == False)
        ]
    )
    iu = len(df[(df["is_valid"] == False) & (df["is_believable"] == False)])
    # iu = len(
    #     df[
    #         (df["is_valid"] == False)
    #         & (df["is_believable"] == False)
    #         & (df["model_pred_is_valid"] != -1)
    #     ]
    # )

    undecided = len(df[df["model_pred_is_valid"] == -1])

    acceptance_rate = {
        "valid_beliebable": vb_valid / vb if vb else 0,
        "valid_unbeliebable": vu_valid / vu if vu else 0,
        "invalid_beliebable": ib_valid / ib if ib else 0,
        "invalid_unbeliebable": iu_valid / iu if iu else 0,
        "undecided": undecided / len(df),
    }

    return df, acceptance_rate, confidences


def get_fb_bi(
    df,
    group_by_names=["is_valid", "is_believable"],
    label_column_name="model_pred_is_valid",
    return_distribution=False,
):
    gb = df.groupby(group_by_names)
    # calculate 95% bootstrapped confidence interval for median
    res = []
    for (is_valid, is_believable), group in gb:
        bootstrap_ci = bootstrap(
            (group[label_column_name],),
            np.mean,
            confidence_level=0.95,
            random_state=1,
            method="percentile",  # "BCa",
            n_resamples=1000,
        )
        res.append(
            {
                "is_valid": is_valid,
                "is_believable": is_believable,
                "low": bootstrap_ci.confidence_interval.low,
                "mean": np.mean(group[label_column_name]),
                "high": bootstrap_ci.confidence_interval.high,
            }
        )
        if return_distribution:
            res[-1]["distribution"] = bootstrap_ci.bootstrap_distribution

    return pd.DataFrame(res)


def get_false_belief_ans_percentage(all_ans, ylabel):
    (
        full_df_treatment,
        acc_rate_treatment,
        confidences_treatment,
    ) = get_fb_acceptance_percentages(
        all_ans["ans_treatment"], all_ans["probs_treatment"]
    )
    (
        full_df_control,
        acc_rate_control,
        confidences_control,
    ) = get_fb_acceptance_percentages(all_ans["ans_control"], all_ans["probs_control"])

    confidences_treatment["Option"] = "Real-life Objects"
    confidences_control["Option"] = "Non-real Objects"
    full_df_treatment["Option"] = "Real-life Objects"
    full_df_control["Option"] = "Non-real Objects"
    full_df = pd.concat([full_df_treatment, full_df_control])
    full_df["is_valid"] = full_df["is_valid"].map({True: "Valid", False: "Invalid"})
    full_df["is_believable"] = full_df["is_believable"].map(
        {True: "Believable", False: "Unbelievable"}
    )
    full_df.rename(
        columns={
            "model_pred_is_valid": "Percentage",
            "is_valid": "Valid",
            "is_believable": "Believable",
            0: "log_prob",
        },
        inplace=True,
    )

    if ylabel == "Accuracy":
        acc_rate_treatment["invalid_beliebable"] = (
            1 - acc_rate_treatment["invalid_beliebable"]
        )
        acc_rate_control["invalid_beliebable"] = (
            1 - acc_rate_control["invalid_beliebable"]
        )

    return (
        list(acc_rate_treatment.values()),
        list(acc_rate_control.values()),
        full_df,
        pd.concat([confidences_treatment, confidences_control]),
    )


def get_false_belief_results(all_ans, ylabel):
    (
        acc_treatment,
        acc_control,
        full_df,
        confidences,
    ) = get_false_belief_ans_percentage(all_ans, ylabel)

    df = pd.DataFrame(
        {
            "Type": [
                "Valid-Believable",
                "Valid-Unbelievable",
                "Invalid-Believable",
                "Invalid-Unbelievable",
                "Undecided",
            ],
            "Real-life Objects": acc_treatment,
            "Non-real Objects": acc_control,
        }
    )

    return df, full_df, confidences


def analyze_false_belief(
    cur_sample,
    model_ans,
    results,
):
    is_valid = cur_sample["metadata"]["is_valid"]
    is_believable = cur_sample["metadata"]["is_believable"]

    ans_meaning = {"is_valid": is_valid, "is_believable": is_believable}
    ans_meaning["model_pred_is_valid"] = model_ans
    results["all_ans_meaning"].append(ans_meaning)

    sample_id = (
        cur_sample["metadata"]["premise_1"],
        cur_sample["metadata"]["premise_2"],
        cur_sample["metadata"]["conclusion"],
    )

    return sample_id, ans_meaning
