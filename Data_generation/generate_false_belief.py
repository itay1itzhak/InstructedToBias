import itertools
import sys

sys.path.append("./")
from Data_generation.samples_classes import *
from Data_generation.templates import *


def switch_a_c(objs):
    A = objs["C"]
    C = objs["A"]
    return A, C


def get_a_b_c(cur_objects, should_switch_a_c):
    if should_switch_a_c:
        A, C = switch_a_c(cur_objects)
    else:
        A = cur_objects["A"]
        C = cur_objects["C"]
    B = cur_objects["B"]
    B_obj = cur_objects["B_Obj"]
    return A, B, C, B_obj


def get_premises(
    A, B, C, B_Obj, is_exp2, is_exp3_switch_inside_syllogisms, is_exp_dm_1, is_exp_dm_2
):
    if is_exp2:
        syllo_1 = ALL_FALSE_BELIEF_SYLLOGISM["some_x_are_y"]
        syllo_2 = ALL_FALSE_BELIEF_SYLLOGISM["no_x_are_y"]
    elif is_exp_dm_1:
        syllo_1 = ALL_FALSE_BELIEF_SYLLOGISM["no_x_are_y"]
        syllo_2 = ALL_FALSE_BELIEF_SYLLOGISM["all_x_are_y"]
    elif is_exp_dm_2:
        syllo_1 = ALL_FALSE_BELIEF_SYLLOGISM["some_x_are_y"]
        syllo_2 = ALL_FALSE_BELIEF_SYLLOGISM["all_x_are_y"]

    else:
        syllo_1 = ALL_FALSE_BELIEF_SYLLOGISM["no_x_are_y"]
        syllo_2 = ALL_FALSE_BELIEF_SYLLOGISM["some_x_are_y"]

    if not is_exp3_switch_inside_syllogisms:
        premise_1 = syllo_1.safe_substitute(X=A, Y=B)
        premise_2 = syllo_2.safe_substitute(X=C, Y=B)
    else:
        premise_1 = syllo_1.safe_substitute(X=B_Obj, Y=A)
        premise_2 = syllo_2.safe_substitute(X=B_Obj, Y=C)

    return premise_1, premise_2


def get_conclusion(
    A: str,
    C: str,
    some_a_are_c: bool,
    is_exp2: bool,
    should_switch_a_c: bool,
):
    syllo_con = ALL_FALSE_BELIEF_SYLLOGISM["some_x_arent_y"]

    if some_a_are_c:
        conclusion = syllo_con.safe_substitute(X=A, Y=C)
        if not should_switch_a_c:
            is_believable = True
        else:
            is_believable = False
        if not is_exp2:
            is_valid = False
        else:
            is_valid = True
    else:
        conclusion = syllo_con.safe_substitute(X=C, Y=A)
        if not should_switch_a_c:
            is_believable = False
        else:
            is_believable = True
        if not is_exp2:
            is_valid = True
        else:
            is_valid = False

    return conclusion, is_believable, is_valid


def add_false_belief_sample(
    all_vals,
    premise_1,
    premise_2,
    conclusion,
    is_believable,
    is_valid,
    conf,
    add_permut,
):
    for closing_line_id, closing_line in ALL_FB_CLOSING_LINES.items():
        all_vals.append(
            {
                "premise_1": premise_1,
                "premise_2": premise_2,
                "conclusion": conclusion,
                "closing_line": closing_line,
                "is_believable": is_believable,
                "is_valid": is_valid,
                "human_or_right_answer": is_valid,
                "are_events_switched": conf["should_switch_a_c"],
                "is_exp2": conf["is_exp2"],
                "is_exp3": conf["is_exp3_switch_inside_syllogisms"],
                "bias_type": conf["bias_type"],
                "is_permuted_option": False,
                "closing_line_id": closing_line_id,
            }
        )
        if add_permut:
            all_vals.append(
                {
                    "premise_1": premise_2,
                    "premise_2": premise_1,
                    "conclusion": conclusion,
                    "closing_line": closing_line,
                    "is_believable": is_believable,
                    "is_valid": is_valid,
                    "human_or_right_answer": is_valid,
                    "are_events_switched": conf["should_switch_a_c"],
                    "is_exp2": conf["is_exp2"],
                    "is_exp3": conf["is_exp3_switch_inside_syllogisms"],
                    "bias_type": conf["bias_type"],
                    "is_permuted_option": True,
                    "closing_line_id": closing_line_id,
                }
            )


def get_dm_1_false_belief_conclusions_options(conf, A, B, C, B_Obj):
    options = []

    # No flowers are animals.
    # All flowers are reptiles
    # Conclusion: No flowers are reptiles.
    premise_1 = ALL_FALSE_BELIEF_SYLLOGISM["no_x_are_y"].safe_substitute(X=A, Y=B)
    premise_2 = ALL_FALSE_BELIEF_SYLLOGISM["all_x_are_y"].safe_substitute(X=C, Y=B)
    conclusion = ALL_FALSE_BELIEF_SYLLOGISM["no_x_are_y"].safe_substitute(X=A, Y=C)
    is_believable = True
    is_valid = True
    options.append(
        {
            "premise_1": premise_1,
            "premise_2": premise_2,
            "conclusion": conclusion,
            "is_believable": is_believable,
            "is_valid": is_valid,
        }
    )
    # No flowers are animals.
    # All reptiles are flowers.
    # Conclusion: No reptiles are animals.
    premise_1 = ALL_FALSE_BELIEF_SYLLOGISM["no_x_are_y"].safe_substitute(X=A, Y=B)
    premise_2 = ALL_FALSE_BELIEF_SYLLOGISM["all_x_are_y"].safe_substitute(X=C, Y=A)
    conclusion = ALL_FALSE_BELIEF_SYLLOGISM["no_x_are_y"].safe_substitute(X=C, Y=B)
    is_believable = False
    is_valid = True
    options.append(
        {
            "premise_1": premise_1,
            "premise_2": premise_2,
            "conclusion": conclusion,
            "is_believable": is_believable,
            "is_valid": is_valid,
        }
    )
    # No flowers are reptiles.
    # All reptiles are animals.
    # Conclusion: No flowers are animals
    premise_1 = ALL_FALSE_BELIEF_SYLLOGISM["no_x_are_y"].safe_substitute(X=A, Y=C)
    premise_2 = ALL_FALSE_BELIEF_SYLLOGISM["all_x_are_y"].safe_substitute(X=C, Y=B)
    conclusion = ALL_FALSE_BELIEF_SYLLOGISM["no_x_are_y"].safe_substitute(X=A, Y=B)
    is_believable = True
    is_valid = False
    options.append(
        {
            "premise_1": premise_1,
            "premise_2": premise_2,
            "conclusion": conclusion,
            "is_believable": is_believable,
            "is_valid": is_valid,
        }
    )
    # No flowers are animals.
    # All flowers are reptiles.
    # Conclusion: No reptiles are animals.
    premise_1 = ALL_FALSE_BELIEF_SYLLOGISM["no_x_are_y"].safe_substitute(X=A, Y=B)
    premise_2 = ALL_FALSE_BELIEF_SYLLOGISM["all_x_are_y"].safe_substitute(X=A, Y=C)
    conclusion = ALL_FALSE_BELIEF_SYLLOGISM["no_x_are_y"].safe_substitute(X=C, Y=B)
    is_believable = False
    is_valid = False
    options.append(
        {
            "premise_1": premise_1,
            "premise_2": premise_2,
            "conclusion": conclusion,
            "is_believable": is_believable,
            "is_valid": is_valid,
        }
    )

    return options


def get_dm_2_false_belief_conclusions_options(conf, A, B, C, B_Obj):
    options = []

    # All diamonds are gems.
    # Some diamonds are transparent things.
    # Conclusion: Some gems are transparent things
    premise_2 = ALL_FALSE_BELIEF_SYLLOGISM["all_x_are_y"].safe_substitute(X=A, Y=C)
    premise_1 = ALL_FALSE_BELIEF_SYLLOGISM["some_x_are_y"].safe_substitute(X=A, Y=B)
    conclusion = ALL_FALSE_BELIEF_SYLLOGISM["some_x_are_y"].safe_substitute(X=C, Y=B)
    is_believable = True
    is_valid = True
    options.append(
        {
            "premise_1": premise_1,
            "premise_2": premise_2,
            "conclusion": conclusion,
            "is_believable": is_believable,
            "is_valid": is_valid,
        }
    )
    # All transparent things are diamonds
    # No gems are diamonds
    # Conclusion: No gems are transparent things
    premise_2 = ALL_FALSE_BELIEF_SYLLOGISM["all_x_are_y"].safe_substitute(X=B, Y=A)
    premise_1 = ALL_FALSE_BELIEF_SYLLOGISM["no_x_are_y"].safe_substitute(X=C, Y=A)
    conclusion = ALL_FALSE_BELIEF_SYLLOGISM["no_x_are_y"].safe_substitute(X=C, Y=B)
    is_believable = False
    is_valid = True
    options.append(
        {
            "premise_1": premise_1,
            "premise_2": premise_2,
            "conclusion": conclusion,
            "is_believable": is_believable,
            "is_valid": is_valid,
        }
    )
    # Some gems are transparent things.
    # All diamonds are gems.
    # Conclusion: Some diamonds are transparent things.
    premise_2 = ALL_FALSE_BELIEF_SYLLOGISM["all_x_are_y"].safe_substitute(X=A, Y=C)
    premise_1 = ALL_FALSE_BELIEF_SYLLOGISM["some_x_are_y"].safe_substitute(X=C, Y=B)
    conclusion = ALL_FALSE_BELIEF_SYLLOGISM["some_x_are_y"].safe_substitute(X=A, Y=B)
    is_believable = True
    is_valid = False
    options.append(
        {
            "premise_1": premise_1,
            "premise_2": premise_2,
            "conclusion": conclusion,
            "is_believable": is_believable,
            "is_valid": is_valid,
        }
    )
    # All transparent things are gems
    # No gems are diamonds
    # Conclusion: No gems are transparent things
    premise_2 = ALL_FALSE_BELIEF_SYLLOGISM["all_x_are_y"].safe_substitute(X=A, Y=C)
    premise_1 = ALL_FALSE_BELIEF_SYLLOGISM["no_x_are_y"].safe_substitute(X=C, Y=A)
    conclusion = ALL_FALSE_BELIEF_SYLLOGISM["no_x_are_y"].safe_substitute(X=C, Y=B)
    is_believable = False
    is_valid = False
    options.append(
        {
            "premise_1": premise_1,
            "premise_2": premise_2,
            "conclusion": conclusion,
            "is_believable": is_believable,
            "is_valid": is_valid,
        }
    )

    return options


def add_dm_false_belief_sample(
    all_vals,
    A,
    B,
    C,
    B_Obj,
    conf,
    add_permut,
):
    if conf["is_exp_dm_1"]:
        options = get_dm_1_false_belief_conclusions_options(conf, A, B, C, B_Obj)
    else:
        options = get_dm_2_false_belief_conclusions_options(conf, A, B, C, B_Obj)

    for opt in options:
        add_false_belief_sample(
            all_vals,
            opt["premise_1"],
            opt["premise_2"],
            opt["conclusion"],
            opt["is_believable"],
            opt["is_valid"],
            conf,
            add_permut,
        )


def add_syllogisms(
    all_vals: list[dict],
    cur_objects: dict,
    add_permut: bool,
    vals_str: str,
    bias_type: Belief_type,
    should_switch_a_c=False,
    is_exp2=False,
    is_exp3_switch_inside_syllogisms=False,
    is_exp_dm_1=False,
    is_exp_dm_2=False,
):
    conf = {
        "should_switch_a_c": should_switch_a_c,
        "is_exp2": is_exp2,
        "is_exp3_switch_inside_syllogisms": is_exp3_switch_inside_syllogisms,
        "is_exp_dm_1": is_exp_dm_1,
        "is_exp_dm_2": is_exp_dm_2,
        "vals_str": vals_str,
        "bias_type": bias_type,
    }

    A, B, C, B_Obj = get_a_b_c(cur_objects, conf["should_switch_a_c"])
    add_dm_false_belief_sample(
        all_vals,
        A,
        B,
        C,
        B_Obj,
        conf,
        add_permut,
    )


def generate_values_false_belief(
    with_bias: bool, bias_type: Belief_type, add_permut: bool
) -> list[dict]:
    all_vals = []
    if with_bias:
        if bias_type == Belief_type.EXP_DM_1:
            all_objects = list(ALL_FB_OBJECTS_BIAS_DM_1.values())
        elif bias_type == Belief_type.EXP_DM_2:
            all_objects = list(ALL_FB_OBJECTS_BIAS_DM_2.values())
        else:
            raise Exception(f"Not supported bias type {bias_type}!")
    else:
        all_objects = list(ALL_FB_OBJECTS_NONSENSE.values())
    vals_str = str(all_objects)

    for cur_objects in all_objects:
        if bias_type == Belief_type.EXP_DM_1:
            add_syllogisms(
                all_vals,
                cur_objects,
                add_permut,
                vals_str,
                bias_type,
                is_exp_dm_1=True,
            )
        if bias_type == Belief_type.EXP_DM_2:
            add_syllogisms(
                all_vals,
                cur_objects,
                add_permut,
                vals_str,
                bias_type,
                is_exp_dm_2=True,
            )
    return all_vals


def get_false_belief_vals(args, bias_types_enums, with_bias):
    all_vals = []
    for bias_type in bias_types_enums:
        curr_bias_type_vals = generate_values_false_belief(
            with_bias,
            bias_type,
            add_permut=args.all_options_permutations,
        )
        all_vals += curr_bias_type_vals
    return all_vals
