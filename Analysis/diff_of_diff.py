import pandas as pd
from statsmodels.formula.api import ols


def convert_decoy_full_df_for_stats(full_df):
    full_df = full_df[["Condition", "Choice"]]
    bias = full_df[full_df["Condition"] == "Decoy Worse than Target"]["Choice"]
    unbiased = full_df[full_df["Condition"] == "No Decoy"]["Choice"]

    bias = bias.map({"competitor": 0, "decoy": 0, "target": 1})
    unbiased = unbiased.map({"competitor": 0, "decoy": 0, "target": 1})

    return bias, unbiased


def convert_certainty_full_df_for_stats(full_df):
    bias = full_df.T["Target is prize with certainty"]
    unbiased = full_df.T["Target is risky too"].dropna()

    bias = bias.map({"better_expected_value": 0, "target": 1})
    unbiased = unbiased.map({"better_expected_value": 0, "target": 1})

    return bias, unbiased


def get_linear_model_diff_of_diff(
    model_one_df_control,
    model_two_df_control,
    model_one_df_treatment,
    model_two_df_treatment,
    pred_label: str,
):
    # group g: 0 control group (not biased), 1 treatment group (biased)
    # t: 0 before treatment (control), 1 after treatment
    # gt: interaction of g * t

    # data before the treatment
    df_before = pd.concat(
        [
            model_one_df_control[[pred_label, "g"]],
            model_two_df_control[[pred_label, "g"]],
        ]
    )
    df_before["t"] = 0
    df_before.columns = ["Predicition", "g", "t"]

    # data after the treatment
    df_after = pd.concat(
        [
            model_one_df_treatment[[pred_label, "g"]],
            model_two_df_treatment[[pred_label, "g"]],
        ]
    )
    df_after["t"] = 1
    df_after.columns = ["Predicition", "g", "t"]

    # data for regression
    df_reg = pd.concat([df_before, df_after])

    # create the interaction
    df_reg["gt"] = df_reg.g * df_reg.t

    # fit the regression
    lin_model = ols("Predicition ~ g + t + gt", data=df_reg).fit()

    return lin_model


def get_false_belief_diff_of_diff(model_one_df, model_two_df):
    model_one_df["g"] = 0
    model_two_df["g"] = 1
    model_one_df["Percentage"] = model_one_df["Percentage"].replace({True: 1, False: 0})
    model_two_df["Percentage"] = model_two_df["Percentage"].replace({True: 1, False: 0})
    model_one_first_treatment = (
        (model_one_df["Valid"] == "Valid")
        & (model_one_df["Believable"] == "Unbelievable")
        & (model_one_df["Option"] == "Real-life Objects")
    )
    model_one_first_control = (model_one_df["Valid"] == "Valid") & (
        model_one_df["Option"] == "Non-Real Objects"
    )
    model_two_first_treatment = (
        (model_two_df["Valid"] == "Valid")
        & (model_two_df["Believable"] == "Unbelievable")
        & (model_two_df["Option"] == "Real-life Objects")
    )
    model_two_first_control = (model_two_df["Valid"] == "Valid") & (
        model_two_df["Option"] == "Non-Real Objects"
    )

    model_one_second_treatment = (
        (model_one_df["Valid"] == "Invalid")
        & (model_one_df["Believable"] == "Believable")
        & (model_one_df["Option"] == "Real-life Objects")
    )
    model_one_second_control = (model_one_df["Valid"] == "Invalid") & (
        model_one_df["Option"] == "Non-Real Objects"
    )
    model_two_second_treatment = (
        (model_two_df["Valid"] == "Invalid")
        & (model_two_df["Believable"] == "Believable")
        & (model_two_df["Option"] == "Real-life Objects")
    )
    model_two_second_control = (model_two_df["Valid"] == "Invalid") & (
        model_two_df["Option"] == "Non-Real Objects"
    )

    # use get_linear_model_diff_of_diff on each of the 2 groups
    ols_1 = get_linear_model_diff_of_diff(
        model_one_df[model_one_first_control],
        model_two_df[model_two_first_control],
        model_one_df[model_one_first_treatment],
        model_two_df[model_two_first_treatment],
        pred_label="Percentage",
    )
    ols_2 = get_linear_model_diff_of_diff(
        model_one_df[model_one_second_control],
        model_two_df[model_two_second_control],
        model_one_df[model_one_second_treatment],
        model_two_df[model_two_second_treatment],
        pred_label="Percentage",
    )

    gt_pvalue_1 = ols_1.pvalues["gt"]
    gt_pvalue_2 = ols_2.pvalues["gt"]
    reg_summery = f"Belief Valid p-value:{gt_pvalue_1:.3f}, Belief Invalid p-value:{gt_pvalue_2:.3f}"

    return reg_summery


def get_decoy_and_certainty_diff_of_diff(bias_name, model_one_df, model_two_df):
    if bias_name == "decoy":
        model_one_df_bias, model_one_df_unbiased = convert_decoy_full_df_for_stats(
            model_one_df
        )
        model_two_df_bias, model_two_df_unbiased = convert_decoy_full_df_for_stats(
            model_two_df
        )
    else:
        (
            model_one_df_bias,
            model_one_df_unbiased,
        ) = convert_certainty_full_df_for_stats(model_one_df)
        (
            model_two_df_bias,
            model_two_df_unbiased,
        ) = convert_certainty_full_df_for_stats(model_two_df)
    model_one_df_unbiased = pd.DataFrame(model_one_df_unbiased)
    model_two_df_unbiased = pd.DataFrame(model_two_df_unbiased)
    model_one_df_bias = pd.DataFrame(model_one_df_bias)
    model_two_df_bias = pd.DataFrame(model_two_df_bias)

    for df in [
        model_one_df_unbiased,
        model_two_df_unbiased,
        model_one_df_bias,
        model_two_df_bias,
    ]:
        df.columns = ["Choice"]

    model_one_df_bias["g"] = 0
    model_one_df_unbiased["g"] = 0
    model_two_df_bias["g"] = 1
    model_two_df_unbiased["g"] = 1

    pred_label = "Choice"
    ols = get_linear_model_diff_of_diff(
        model_one_df_unbiased,
        model_two_df_unbiased,
        model_one_df_bias,
        model_two_df_bias,
        pred_label=pred_label,
    )

    gt_pvalue = ols.pvalues["gt"]
    reg_summery = f"{gt_pvalue:.3f}"

    return reg_summery


def get_diff_of_diff(bias_name, model_one_df, model_two_df):
    if bias_name == "false_belief":
        reg_summery = get_false_belief_diff_of_diff(model_one_df, model_two_df)
    else:
        reg_summery = get_decoy_and_certainty_diff_of_diff(
            bias_name, model_one_df, model_two_df
        )

    return reg_summery
