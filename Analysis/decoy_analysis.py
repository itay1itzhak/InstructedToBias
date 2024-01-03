from scipy.stats import bootstrap
import numpy as np
import pandas as pd


def get_decoy_ans_percentage(all_ans):
    ans_treatment = all_ans["ans_treatment"]
    ans_control = all_ans["ans_control"]
    n_treatment = len(ans_treatment)
    n_control = len(ans_control)

    competitor = [
        ans_treatment.count("competitor") / n_treatment,
        ans_control.count("competitor") / n_control,
    ]
    target = [
        ans_treatment.count("target") / n_treatment,
        ans_control.count("target") / n_control,
    ]
    decoy = [
        ans_treatment.count("decoy") / n_treatment,
        ans_control.count("decoy") / n_control,
    ]
    undecided = [
        ans_treatment.count("-1") / n_treatment,
        ans_control.count("-1") / n_control,
    ]

    return competitor, target, decoy, undecided


def get_decoy_results(all_ans):
    competitor, target, decoy, undecided = get_decoy_ans_percentage(all_ans)

    full_df = pd.DataFrame.from_dict(
        {
            "Decoy Worse than Target": all_ans["ans_treatment"],
            "Probabilities Decoy Worse than Target": all_ans["probs_treatment"],
            "No Decoy": all_ans["ans_control"],
            "Probabilities No Decoy": all_ans["probs_control"],
        },
        orient="index",
    )

    confidences = get_decoy_bi(full_df)

    full_df = (
        full_df.T.melt()
        .rename(columns={"variable": "Condition", "value": "Choice"})
        .dropna()
    )
    # Convert the 'res' column into dummy/indicator variables
    dummies = pd.get_dummies(full_df["Choice"]).astype(bool)
    # Concatenate the original DataFrame with the new dummy columns
    full_df = pd.concat([full_df, dummies], axis=1)

    df = pd.DataFrame(
        {
            "Type": [
                "Decoy Worse than Target",
                "No Decoy",
            ],
            "Competitor": competitor,
            "Target": target,
            "Decoy": decoy,
            "Undecided": undecided,
        }
    )

    return df, full_df, confidences


def get_decoy_bi(df):
    # calculate 95% bootstrapped confidence interval for mean
    res = []
    row_index = 0
    # for exp_name, row in df.iterrows():
    while row_index < len(df):
        row = df.iloc[row_index]
        probs_row = df.iloc[row_index + 1]
        exp_name = row.name

        for current_option in ["competitor", "target", "decoy"]:
            option_mean = np.mean(row.dropna() == current_option)
            if len(probs_row.dropna()[row.dropna() == current_option]) == 0:
                option_log_prob_mean = float("-inf")
            else:
                try:
                    option_log_prob_sum = np.logaddexp.reduce(
                        probs_row.dropna()[row.dropna() == current_option].to_numpy(
                            dtype="float64"
                        )
                    )
                    option_log_prob_mean = option_log_prob_sum - np.log(
                        len(probs_row.dropna()[row.dropna() == current_option])
                    )
                except RuntimeWarning:
                    raise Exception("option_log_prob_mean has failed to calculate!")

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


def analyze_decoy_answer(
    cur_sample: dict,
    model_ans: int,
    results: dict,
):
    competitor_location = cur_sample["metadata"]["competitor"]
    target_location = cur_sample["metadata"]["target"]
    decoy_location = cur_sample["metadata"]["decoy"]

    if model_ans == competitor_location:
        ans_meaning = "competitor"
    elif model_ans == target_location:
        ans_meaning = "target"
    elif model_ans == decoy_location:
        ans_meaning = "decoy"
    else:  # model is undecided
        ans_meaning = "-1"

    results["all_ans_meaning"].append(ans_meaning)

    results["price_target"].append(cur_sample["metadata"][f"price{target_location}"])
    results["price_competitor"].append(
        cur_sample["metadata"][f"price{competitor_location}"]
    )

    # to check agreement between similar content samples, we need to identify them
    # similar samples are identified by  having the same following features:
    sample_id = frozenset(
        (
            # cur_sample["metadata"]["product"],
            # cur_sample["metadata"]["quality_measurment"],
            # "price1" + str(cur_sample["metadata"]["price1"]),
            # "price2" + str(cur_sample["metadata"]["price2"]),
            # "price3" + str(cur_sample["metadata"]["price3"]),
            # "quality1" + str(cur_sample["metadata"]["quality1"]),
            # "quality2" + str(cur_sample["metadata"]["quality2"]),
            # "quality3" + str(cur_sample["metadata"]["quality3"]),
            # "template" + str(cur_sample["metadata"]["template"]),
            "permutation_id"
            + str(cur_sample["metadata"]["permutation_id"]),
        )
    )

    return sample_id, ans_meaning
