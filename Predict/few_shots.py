import random

from Data_generation.generate_false_belief import add_syllogisms
from Data_generation.samples_classes import Belief_type, SamplesGen
from Data_generation.templates import (
    ALL_DECOY_TWO_OPTIONS_FORMAT_FEW_SHOT,
    ALL_DECOY_TEMP_TWO_OPTIONS,
    ALL_DECOY_THREE_OPTIONS_FORMAT_FEW_SHOT,
    ALL_DECOY_TEMP_THREE_OPTIONS,
    ALL_FB_OBJECTS_TASK_FEW_SHOT,
    CERTAINTY_TEMPLATES,
    ALL_FALSE_BELIEF_DEEPMIND_TEMP,
    ALL_FB_FORMAT_FEW_SHOT,
)


def get_decoy_few_shots_temp_and_options(data_path, with_format_few_shot):
    all_values = None
    if "only_two_options" in data_path:
        if with_format_few_shot:
            all_temps = list(ALL_DECOY_TWO_OPTIONS_FORMAT_FEW_SHOT.values())
        else:
            all_temps = list(ALL_DECOY_TEMP_TWO_OPTIONS.values())
        options = ["1", "2"]
    else:  # three options
        if with_format_few_shot:
            all_temps = list(ALL_DECOY_THREE_OPTIONS_FORMAT_FEW_SHOT.values())
        else:
            all_temps = list(ALL_DECOY_TEMP_THREE_OPTIONS.values())
        options = ["1", "2", "3"]

    return all_temps, options, all_values


def get_certainty_few_shots_temp_and_options():
    all_temps = list(CERTAINTY_TEMPLATES["CERTAINTY_BIAS_MEGA"].values())
    all_values = list(
        CERTAINTY_TEMPLATES["ALL_CERTAINTY_FORMAT_FEW_SHOT_OBJECTS"].values()
    )
    options = ["A", "B"]

    return all_temps, options, all_values


def get_false_belief_few_shots_temp_and_options(data_path, with_format_few_shot):
    all_temps = list(ALL_FALSE_BELIEF_DEEPMIND_TEMP.values())

    # if we do not use the original deepmind data, we can use our own data that recreate the same effect
    if "dm_full" not in data_path:
        options = [Belief_type.EXP_DM_1.name, Belief_type.EXP_DM_2.name]
    else:  # "dm_full" in data_path:
        options = [Belief_type.EXP_DM_FULL.name]

    # if task few use the task few shot objects, else use the format few shot objects
    if with_format_few_shot:
        all_values = list(ALL_FB_FORMAT_FEW_SHOT.values())
        options = ["CONCLUSION_VALID", "CONCLUSION_INVALID"]
    else:
        all_values = list(ALL_FB_OBJECTS_TASK_FEW_SHOT.values())

    return all_temps, options, all_values


def get_few_shots_temp_and_options(bias_name, data_path, with_format_few_shot):
    if bias_name == "decoy":
        all_temps, options, all_values = get_decoy_few_shots_temp_and_options(
            data_path, with_format_few_shot
        )
    elif bias_name == "certainty":
        all_temps, options, all_values = get_certainty_few_shots_temp_and_options()
    elif bias_name == "false_belief":
        (
            all_temps,
            options,
            all_values,
        ) = get_false_belief_few_shots_temp_and_options(data_path, with_format_few_shot)
    else:
        raise Exception(f"Not supported bias {bias_name}")

    return all_temps, options, all_values


def get_false_belief_sample(all_vals, exp_options, e, prev_sample):
    cur_vals = []
    cur_objects = random.choice(list(ALL_FB_OBJECTS_TASK_FEW_SHOT.values()))
    bias_type = random.choice(exp_options)
    add_syllogisms(
        cur_vals,
        cur_objects,
        add_permut=True,
        vals_str="",
        bias_type=bias_type,
    )
    # all_vals.append(random.choice(cur_vals))
    for sample in cur_vals:
        sample["closing_line"] = e["closing_line"]
    gen = SamplesGen(
        "false_belief", [e["template"]], cur_vals, [bias_type], with_bias=False
    )

    sample = random.choice(gen.generate_samples())
    if all_vals:  # if we already have a sample
        # get sample that is different from the previous one
        while sample.values["is_valid"] == prev_sample.values["is_valid"]:  # type: ignore
            sample = random.choice(gen.generate_samples())

    return sample


def get_false_belief_task_few_shot(e, exp_options, k_shot) -> list[str]:
    all_vals = []
    prev_sample = None
    for k in range(k_shot):
        sample = get_false_belief_sample(all_vals, exp_options, e, prev_sample)
        prev_sample = sample
        # if sample.values["is_valid"]:
        #     sample_text = sample.get_text() + " The conclusion is valid."
        # else:
        #     sample_text = sample.get_text() + " The conclusion is invalid."
        # all_vals.append(sample_text)
        sample_answer = (
            " The conclusion is valid."
            if sample.values["is_valid"]
            else " The conclusion is invalid."
        )
        all_vals.append({"question": sample.get_text(), "answer": sample_answer})
    return all_vals


def get_by_templates_few_shot(
    e, all_temps, all_values, bias_name, options, k_shot
) -> list[str]:
    if bias_name == "decoy":
        chosen_templates = random.sample(
            all_temps, k_shot
        )  # choose three unique example
    else:
        chosen_templates = [
            all_temps[int(e["template"]) - 1]
        ] * k_shot  # choose the same template as the original sample
    if all_values:
        chosen_values = random.sample(all_values, k_shot)
    else:
        chosen_values = [None]
    random.shuffle(options)

    if bias_name == "decoy":
        # few_shots_texts = [
        #     shot_template.substitute(OPTION=options[i % 2])  # type: ignore
        #     for i, shot_template in enumerate(chosen_templates)
        # ]
        few_shots_texts = [
            {
                **shot_template,
                "answer": shot_template["answer"].substitute(OPTION=options[i % 2]),
            }
            for i, shot_template in enumerate(chosen_templates)
        ]

    elif bias_name == "certainty":
        if chosen_values:
            for vals in chosen_values:
                random.shuffle(vals)
        few_shots_texts = [
            {
                "question": shot_template.substitute(  # type: ignore
                    # OPTION=options[i % 2],
                    FIRST_OPTION_OPENING=e["first_option_opening"],
                    SECOND_OPTION_OPENING=e["second_option_opening"],
                    FIRST_OPTION=chosen_values[i][0],
                    SECOND_OPTION=chosen_values[i][1],
                    # OPENING_LINE=e["text"].split('\n')[0],
                    # CLOSING_LINE=e["closing_line"],
                ),
                "answer": f" Option {options[i % 2]}.",
            }
            for i, shot_template in enumerate(chosen_templates)
        ]
    elif bias_name == "false_belief":
        few_shots_texts = get_false_belief_task_few_shot(
            e, options, len(chosen_templates)
        )
    else:
        raise Exception(f"Not supported bias {bias_name}")

    return few_shots_texts  # type: ignores


def not_same_template_or_same_example(e, sample_e, bias_name):
    if bias_name == "certainty":
        same_template = (
            e["template"] == sample_e["template"]
            and e["subtemplates"]["options_text_template_id"]
            == sample_e["subtemplates"]["options_text_template_id"]
            and e["subtemplates"]["options_a_template_id"]
            == sample_e["subtemplates"]["options_a_template_id"]
            and e["subtemplates"]["options_b_template_id"]
            == sample_e["subtemplates"]["options_b_template_id"]
        )
        same_example = (
            e["option_a"] == sample_e["option_a"]
            and e["option_b"] == sample_e["option_b"]
        ) or (
            e["option_a"] == sample_e["option_b"]
            and e["option_b"] == sample_e["option_a"]
        )
        return not same_template or same_example
    else:
        raise Exception(f"Not supported bias {bias_name}")


def get_task_few_shot(e, examples, k_shot, bias_name, options):
    """
    sample a random example from the same template
    """
    random.shuffle(options)
    all_shots = []
    for i in range(k_shot):
        sample_e = random.choice(list(examples.values()))
        # look a different example from e and from other shots
        while (
            not_same_template_or_same_example(e, sample_e, bias_name)
            or sample_e["text"] in all_shots
        ):
            sample_e = random.choice(list(examples.values()))
        all_shots.append(sample_e["text"])
    few_shots_texts = [
        {"question": sample_e, "answer": f" Option {options[i % 2]}."}
        for i, sample_e in enumerate(all_shots)
    ]

    return few_shots_texts


def get_false_belief_format_few_shot(e, k_shot, all_values, options):
    """
    sample a random k_shot examples from ALL_FB_TASK_FEW_SHOT,
    then choose for each k_shot example a random valid or invalid conclusion,
    fit it to the same template as e,
    return the list of few-shot examples.
    """
    chosen_values = random.sample(all_values, k_shot)
    all_shots = []
    for cur_value in chosen_values:
        is_valid = random.sample(options, 1)[0]
        template = ALL_FALSE_BELIEF_DEEPMIND_TEMP[e["template"]]

        answer = (
            " The conclusion is valid." if is_valid else " The conclusion is invalid."
        )

        all_shots.append(
            {
                "question": template.substitute(
                    PREMISE1=cur_value["PREMISE1"],
                    PREMISE2=cur_value["PREMISE2"],
                    CONCLUSION=cur_value[is_valid],
                    CLOSING_LINE=e["closing_line"],
                ),
                "answer": answer,
            }
        )

    return all_shots


def get_few_shot_text(
    with_format_few_shot,
    with_task_few_shot,
    e,
    examples,
    k_shot,
    bias_name,
    all_temps,
    all_values,
    options,
):
    """
    return a list of few shot texts
    """
    if with_format_few_shot:
        if bias_name == "false_belief":
            few_shots_texts = get_false_belief_format_few_shot(
                e,
                k_shot,
                all_values,
                options,
            )
        else:
            few_shots_texts = get_by_templates_few_shot(
                e,
                all_temps,
                all_values,
                bias_name,
                options,
                k_shot,
            )
    elif with_task_few_shot:
        if bias_name == "false_belief":
            few_shots_texts = get_by_templates_few_shot(
                e,
                all_temps,
                all_values,
                bias_name,
                options,
                k_shot,
            )
        else:
            few_shots_texts = get_task_few_shot(
                e,
                examples,
                k_shot,
                bias_name,
                options,
            )
    else:
        raise Exception(
            f"Not supported this kind of few shot yet {with_format_few_shot =} {with_task_few_shot =}"
        )

    return few_shots_texts
