import itertools
import copy
import numpy as np
from Data_generation.certainty_values import (
    get_certainty_bias_three_options,
    get_certainty_not_bias_three_options,
    get_certainty_bias_two_options,
    get_certainty_not_bias_two_options,
    get_certainty_bias_not_probable_options,
    get_certainty_not_bias_not_probable_options,
)
from samples_classes import Certainty_type
from templates import CERTAINTY_TEMPLATES


def build_option(
    vals,
    option_template,
    option_type,
    input_val_keys_list,
    output_wanted_keys_list=None,
):
    """
    input_val_keys_list - list of keys in vals dict
    output_wanted_keys_list - list of keys wanted in option_template
    """
    output_wanted_keys_list = (
        input_val_keys_list
        if output_wanted_keys_list is None
        else output_wanted_keys_list
    )
    option = {
        wanted_key: vals[val_key]
        for val_key, wanted_key in zip(input_val_keys_list, output_wanted_keys_list)
    }
    option_text = option_template.safe_substitute(**option)
    option["option_text"] = option_text
    option["option_type"] = option_type
    return option


def get_certainty_options_dict(
    vals,
    option_a_template,
    option_b_template,
    input_keys_a,
    input_keys_b,
    output_keys_b,
):
    # build option a
    option_a = build_option(
        vals,
        option_a_template,
        "better_expected_value",
        input_keys_a,
    )

    # build option b
    option_b = build_option(
        vals,
        option_b_template,
        "target",
        input_keys_b,
        output_wanted_keys_list=output_keys_b,
    )

    return option_a, option_b


def get_certainty_options_division(
    bias_type,
    with_bias,
    option_a_template,
    option_b_template,
    vals,
):
    if bias_type == Certainty_type.DEVIDE_OPTION_A_TO_THREE_PROBS and with_bias:
        return get_certainty_options_dict(
            vals,
            option_a_template,
            option_b_template,
            ["PROB1", "PRIZE1", "PROB2", "PRIZE2", "PROB3", "PRIZE3"],
            ["PROB4", "PRIZE4"],
            ["PROB1", "PRIZE1"],
        )
    elif bias_type == Certainty_type.DEVIDE_OPTION_A_TO_THREE_PROBS and not with_bias:
        return get_certainty_options_dict(
            vals,
            option_a_template,
            option_b_template,
            ["PROB1", "PRIZE1", "PROB2", "PRIZE2"],
            ["PROB3", "PRIZE3", "PROB4", "PRIZE4"],
            ["PROB1", "PRIZE1", "PROB2", "PRIZE2"],
        )

    elif bias_type == Certainty_type.DEVIDE_OPTION_A_TO_TWO_PROBS and with_bias:
        return get_certainty_options_dict(
            vals,
            option_a_template,
            option_b_template,
            ["PROB1", "PRIZE1", "PROB2", "PRIZE2"],
            ["PROB3", "PRIZE3"],
            ["PROB1", "PRIZE1"],
        )
    elif bias_type == Certainty_type.DEVIDE_OPTION_A_TO_TWO_PROBS and not with_bias:
        return get_certainty_options_dict(
            vals,
            option_a_template,
            option_b_template,
            ["PROB1", "PRIZE1", "PROB2", "PRIZE2"],
            ["PROB3", "PRIZE3", "PROB4", "PRIZE4"],
            ["PROB1", "PRIZE1", "PROB2", "PRIZE2"],
        )
    elif bias_type == Certainty_type.NOT_PROBABLE:  # and with_bias:
        return get_certainty_options_dict(
            vals,
            option_a_template,
            option_b_template,
            ["PROB1", "PRIZE1", "PROB2", "PRIZE2"],
            ["PROB3", "PRIZE3", "PROB4", "PRIZE4"],
            ["PROB1", "PRIZE1", "PROB2", "PRIZE2"],
        )
    else:
        raise NameError(
            f"Unsupported bias type and with/without bias {bias_type}, with_bias={with_bias}"
        )


def check_bad_text(text):
    return "-1" in text or "PRIZE" in text or "PROB" in text


def get_all_options_permutations(
    bias_type,
    with_bias,
    option_a_template,
    option_b_template,
    vals,
    all_options_permutations,
):
    option_a, option_b = get_certainty_options_division(
        bias_type,
        with_bias,
        option_a_template,
        option_b_template,
        vals,
    )

    all_probs_prizes = [option_a, option_b]

    if any(check_bad_text(option["option_text"]) for option in all_probs_prizes):
        raise NameError("Bad text was detected in option text!")

    if all_options_permutations:
        all_options = list(itertools.permutations(all_probs_prizes))
    else:
        all_options = [all_probs_prizes]

    return all_options


def get_certainty_ans_indices(
    with_bias, options_permuted, permutation_index, subtemplates
):
    better_expected_value_index = -1
    target_index = -1
    subtemplates["permutation_index"] = permutation_index + 1

    for i, p in enumerate(options_permuted):
        if p["option_type"] == "better_expected_value":
            better_expected_value_index = i
        if p["option_type"] == "target":
            target_index = i

    if with_bias:
        human_or_right_answer = target_index
    else:
        human_or_right_answer = better_expected_value_index

    return human_or_right_answer, better_expected_value_index, target_index


def add_certainty_values_different_permutations(
    values,
    bias_type,
    with_bias,
    vals,
    vals_str,
    template,
    first_option_opening,
    second_option_opening,
    option_a_template,
    option_b_template,
    subtemplates,
    all_options_permutations,
):
    all_options = get_all_options_permutations(
        bias_type,
        with_bias,
        option_a_template,
        option_b_template,
        vals,
        all_options_permutations,
    )

    for permutation_index, options_permuted in enumerate(all_options):
        (
            human_or_right_answer,
            better_expected_value_index,
            target_index,
        ) = get_certainty_ans_indices(
            with_bias, options_permuted, permutation_index, subtemplates
        )

        values.append(
            {
                "template": template,
                "subtemplates": copy.deepcopy(subtemplates),
                "first_option_opening": first_option_opening,
                "second_option_opening": second_option_opening,
                "option_a": options_permuted[0],
                "option_b": options_permuted[1],
                "vals_range": vals_str,
                "bias_type": bias_type,
                "human_or_right_answer": human_or_right_answer + 1,
                "better_expected_value": better_expected_value_index + 1,
                "target": target_index + 1,
            }
        )

    return values


def get_val_str(all_gen_vals):
    for v in all_gen_vals.values():
        assert len(v) == len(all_gen_vals["first_probs"])
    vals_str = "".join([str(v) for v in all_gen_vals.values()])
    return vals_str


def get_all_values(prizes, probs):
    if len(prizes) == 4:
        vals = [
            f"${prizes[0][i]},{probs[0][i]}%,${prizes[1][i]},{probs[1][i]}%,${prizes[2][i]},{probs[2][i]}%,${prizes[3][i]},{probs[3][i]}%"
            for i in range(len(prizes[0]))
        ]
    elif len(prizes) == 3:
        vals = [
            f"${prizes[0][i]},{probs[0][i]}%,${prizes[1][i]},{probs[1][i]}%,${prizes[2][i]},{probs[2][i]}%,-1,-1"
            for i in range(len(prizes[0]))
        ]

    return vals


def generate_values_certainty(with_bias, b_type):
    all_vals_str = ""
    all_vals = []

    if with_bias and b_type == Certainty_type.DEVIDE_OPTION_A_TO_THREE_PROBS:
        all_gen_vals, prizes, probs = get_certainty_bias_three_options()
    elif not with_bias and b_type == Certainty_type.DEVIDE_OPTION_A_TO_THREE_PROBS:
        all_gen_vals, prizes, probs = get_certainty_not_bias_three_options()
    elif with_bias and b_type == Certainty_type.DEVIDE_OPTION_A_TO_TWO_PROBS:
        all_gen_vals, prizes, probs = get_certainty_bias_two_options()
    elif not with_bias and b_type == Certainty_type.DEVIDE_OPTION_A_TO_TWO_PROBS:
        all_gen_vals, prizes, probs = get_certainty_not_bias_two_options()
    elif with_bias and b_type == Certainty_type.NOT_PROBABLE:
        all_gen_vals, prizes, probs = get_certainty_bias_not_probable_options()
    elif not with_bias and b_type == Certainty_type.NOT_PROBABLE:
        all_gen_vals, prizes, probs = get_certainty_not_bias_not_probable_options()
    else:
        raise NameError(f"certainty type is not supported, b_type - {b_type}")

    all_vals_str = get_val_str(all_gen_vals)
    all_vals = get_all_values(prizes, probs)

    return all_vals, all_vals_str


def get_certainty_options_templates(with_bias, bias_type, bias_types_enums):
    all_option_a_templates = []
    all_option_b_templates = []

    if with_bias:
        if bias_type == Certainty_type.DEVIDE_OPTION_A_TO_THREE_PROBS:
            all_option_a_templates = CERTAINTY_TEMPLATES[
                "OPTION_UNBIAS_CERTAINTY_THREE"
            ].items()
            all_option_b_templates = CERTAINTY_TEMPLATES[
                "OPTION_BIAS_CERTAINTY_ONE"
            ].items()
        elif bias_type == Certainty_type.DEVIDE_OPTION_A_TO_TWO_PROBS:
            all_option_a_templates = CERTAINTY_TEMPLATES[
                "OPTION_UNBIAS_CERTAINTY_TWO"
            ].items()
            all_option_b_templates = CERTAINTY_TEMPLATES[
                "OPTION_BIAS_CERTAINTY_ONE"
            ].items()
        elif bias_type == Certainty_type.NOT_PROBABLE:
            all_option_a_templates = CERTAINTY_TEMPLATES[
                "OPTION_UNBIAS_CERTAINTY_TWO"
            ].items()
            all_option_b_templates = CERTAINTY_TEMPLATES[
                "OPTION_UNBIAS_CERTAINTY_TWO"
            ].items()
    else:
        all_option_a_templates = CERTAINTY_TEMPLATES[
            "OPTION_UNBIAS_CERTAINTY_TWO"
        ].items()
        all_option_b_templates = CERTAINTY_TEMPLATES[
            "OPTION_UNBIAS_CERTAINTY_TWO"
        ].items()

    if not all_option_a_templates or not all_option_b_templates:
        raise NameError(
            f"certainty type is not supported, bias_types_enums - {bias_types_enums}"
        )

    return all_option_a_templates, all_option_b_templates


def generate_certainty_subtemplates(
    with_bias, bias_type, num_of_subtemplates, bias_types_enums
):
    (
        all_option_a_templates,
        all_option_b_templates,
    ) = get_certainty_options_templates(with_bias, bias_type, bias_types_enums)

    all_text_options = list(
        itertools.product(
            CERTAINTY_TEMPLATES["ALL_OPTIONS_TEXT_CERTAINTY"].items(),
            all_option_a_templates,
            all_option_b_templates,
        )
    )

    all_text_options = all_text_options[:num_of_subtemplates]
    return all_text_options


def vals_to_dict(vals):
    return {
        "PRIZE1": vals[0],
        "PROB1": vals[1],
        "PRIZE2": vals[2],
        "PROB2": vals[3],
        "PRIZE3": vals[4],
        "PROB3": vals[5],
        "PRIZE4": vals[6],
        "PROB4": vals[7],
    }


def get_certainty_vals(args, bias_types_enums, with_bias):
    values = []
    for bias_type_index, bias_type in enumerate(bias_types_enums):
        all_vals, vals_str = generate_values_certainty(with_bias, bias_type)
        all_text_options = generate_certainty_subtemplates(
            with_bias, bias_type, args.num_of_subtemplates, bias_types_enums
        )

        for vals_index, vals in enumerate(all_vals):
            vals = vals_to_dict(vals.split(","))
            for (
                options_text,
                option_a_template,
                option_b_template,
            ) in all_text_options:
                subtemplates = {
                    "bias_type_index": bias_type_index + 1,
                    "vals_index": vals_index + 1,
                    "options_text_template_id": options_text[0],
                    "options_a_template_id": option_a_template[0],
                    "options_b_template_id": option_b_template[0],
                }
                add_certainty_values_different_permutations(
                    values,
                    bias_type,
                    with_bias,
                    vals,
                    vals_str,
                    args.templates,
                    options_text[1][0],
                    options_text[1][1],
                    option_a_template[1],
                    option_b_template[1],
                    subtemplates,
                    args.all_options_permutations,
                )
    return values
