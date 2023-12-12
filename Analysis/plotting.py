import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from utils import get_map_model_names


def preprocess_data(full_df, confidences, bias_name, values_list):
    if bias_name == "decoy" or bias_name == "certainty":
        confidences = confidences.astype({"mean": float, "low": float, "high": float})
        confidences["ci_95_low"] = confidences["mean"] - confidences["low"]
        confidences["ci_95_high"] = confidences["high"] - confidences["mean"]
        plot_df = confidences.copy()
        if bias_name == "certainty":
            plot_df["Condition"] = plot_df["Condition"].replace(
                {
                    "Target is prize with certainty": "Treatment",
                    "Target is risky too": "Control",
                }
            )
            plot_df["model_pred"] = plot_df["model_pred"].replace(
                {
                    "better_expected_value": "Better Value",
                    "target": "Target",
                }
            )
        colors = (
            ["tab:red", "tab:blue"]
            if bias_name == "certainty"
            else ["tab:red", "tab:green", "tab:blue"]
        )
    elif bias_name == "false_belief":
        plot_df = full_df.loc[full_df["Percentage"] != -1].copy()
        plot_df.loc[
            plot_df["Option"] == "Non-real Objects", "Believable"
        ] = "Unbelievable"
        plot_df["Type"] = plot_df.apply(
            lambda row: row["Believable"]
            if row["Option"] == "Real-life Objects"
            else "Control",
            axis=1,
        )
        colors = ["tab:green", "tab:red", "tab:blue"]
    else:
        raise Exception(f"Not supported bias name = {bias_name}")

    return plot_df, colors


def plot_histogram(
    plot_df,
    bias_name,
    model,
    fig_f_name,
    plot_ylabel="Percentage Of Choices",
    colors=None,
):
    sns.set_theme(style="darkgrid")
    sns.set_context("paper", font_scale=2)
    sns.set_palette("dark")

    if bias_name == "false_belief":
        out = sns.barplot(
            data=plot_df,
            x="Valid",
            y="Percentage",
            errorbar=("ci", 95),
            hue="Type",
            alpha=0.8,
            palette=colors,
            edgecolor="black",
        )
        plt.xlabel(get_map_model_names()[model])
    else:
        out = sns.barplot(
            x="model_pred",
            y="mean",
            hue="Condition",
            data=plot_df,
            alpha=0.9,
            palette=colors,
            edgecolor="black",
        )
        yerr = np.array([plot_df["ci_95_low"], plot_df["ci_95_high"]])
        x_coords = [p.get_x() + 0.5 * p.get_width() for p in out.patches]
        y_coords = [p.get_height() for p in out.patches]
        out.errorbar(x=x_coords, y=y_coords, yerr=yerr, fmt="none", c="k")
        plt.xlabel("Option")

    plt.ylabel(plot_ylabel)
    plt.legend(bbox_to_anchor=(1.22, 0.98), loc="upper right", borderaxespad=1)
    plt.savefig(fig_f_name, bbox_inches="tight")
    plt.clf()


def save_plot_hist(
    full_df,
    confidences,
    bias_name,
    values_list,
    model,
    fig_f_name,
    plot_ylabel="Percentage Of Choices",
):
    """
    plot histogram for decoy and certainty biases for a single experiment
    """
    plot_df, colors = preprocess_data(full_df, confidences, bias_name, values_list)
    plot_histogram(plot_df, bias_name, model, fig_f_name, plot_ylabel, colors)


def plot_bias_scores(results_df):
    plt.axhline(y=0.0, color="r", linestyle="--")
    sns.lineplot(
        x="model",
        y="Belief Valid",
        data=results_df,
        label="Valid Bias",
        linewidth=1.5,
    )
    ax = sns.lineplot(
        x="model",
        y="Belief Invalid",
        data=results_df,
        label="Invalid Bias",
        linewidth=1.5,
    )
    plt.ylabel("Bias Scores")
    return ax


def plot_acceptance_rates(results_df):
    plt.axhline(y=0.5, color="r", linestyle="--")
    sns.lineplot(
        x="model",
        y="real_valid_acceptance",
        data=results_df,
        label="Real Valid",
        linewidth=1.5,
    )
    sns.lineplot(
        x="model",
        y="non_real_valid_acceptance",
        data=results_df,
        label="Non-Real Valid",
        linewidth=1.5,
    )
    sns.lineplot(
        x="model",
        y="real_invalid_acceptance",
        data=results_df,
        label="Real Invalid",
        linewidth=1.5,
    )
    ax = sns.lineplot(
        x="model",
        y="non_real_invalid_acceptance",
        data=results_df,
        label="Non-Real Invalid",
        linewidth=1.5,
    )
    plt.ylabel("Acceptance Rate")
    return ax


def save_belief_plot(experiment_args, ax, all_models, file_suffix):
    # Save the plot
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper right", borderaxespad=1)
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
    file_suffix += experiment_args["comments_results_name"]

    plt.savefig(
        experiment_args["logging_path"]
        .with_stem(file_suffix + f"_{str(all_models)}")
        .with_suffix(".png")
    )
    plt.clf()


def plot_false_belief(comparing_dict, experiment_args, all_models):
    plt.clf()

    comparing_dict["model"] = comparing_dict["model"].map(get_map_model_names())
    ax_bias_scores = plot_bias_scores(comparing_dict)
    save_belief_plot(
        experiment_args,
        ax_bias_scores,
        all_models,
        file_suffix="bias_scores",
    )
    ax_acceptance_rates = plot_acceptance_rates(comparing_dict)
    save_belief_plot(
        experiment_args,
        ax_acceptance_rates,
        all_models,
        file_suffix="acceptance_rates",
    )
