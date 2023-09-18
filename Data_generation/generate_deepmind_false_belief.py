import os
import json
from pathlib import Path
import pandas as pd
from templates import TEMP_FALSE_BELIEF_OPENING_LINES

input_file = Path("Data/false_belief/syllogism_problems/syllogism_problems.json")
output_file = Path(
    "Data/false_belief/all_permutations/t_[1, 2, 3, 4, 5, 6, 7]_dm_full.json"
)

with open(input_file) as f:
    data = json.load(f)

all_templates = {
    "none": 5,
    "evaluate_arguments": 6,
    "logic_problems": 7,
}


for with_bias in [True, False]:
    output = {}
    sample_num = 0
    for item in data:
        if with_bias == item["is_realistic"]:
            item_processed = {}
            is_valid = (
                "invalid" not in item["correct_answer"][0]
                and "invalid" not in item["correct_answer"]
            )
            is_consistent = item["is_consistent"]
            text = item["input"]
            text_lines = text.split("\n")
            argument_line = text_lines.index("Argument:")

            item_processed["premise_1"] = text_lines[argument_line + 1]
            item_processed["premise_2"] = text_lines[argument_line + 2]
            item_processed["conclusion"] = text_lines[argument_line + 3].replace(
                "Conclusion: ", ""
            )
            item_processed["is_valid"] = is_valid

            old_condition = is_valid == is_consistent
            new_condition = (is_valid and is_consistent) or (
                not is_valid and is_consistent
            )
            # if old_condition != new_condition:
            #     print(text)
            #     print(f"{old_condition =}, {is_valid=}, {is_consistent=}")
            #     print(f"{new_condition =}, {is_valid=}, {is_consistent=}")
            #     print("+" * 50)
            item_processed[
                "is_believable"
            ] = new_condition  # (is_consistent and is_valid) or (not is_consistent and not is_valid)
            item_processed["human_or_right_answer"] = is_valid  # == is_consistent
            item_processed["is_permuted_option"] = item["order_first"]
            item_processed["template"] = all_templates[item["initial_prompt"]]
            item_processed["with_bias"] = with_bias
            item_processed["text"] = text

            item_processed["are_events_switched"] = False
            item_processed["is_exp2"] = False
            item_processed["is_exp3"] = False
            item_processed["bias_type"] = "Belief_type.EXP_DM_FULL"
            item_processed["bias_name"] = "false_belief"
            item_processed["closing_line"] = "Answer:"
            item_processed["closing_line_id"] = 1

            output[sample_num] = item_processed
            sample_num += 1
            if item["initial_prompt"] == "none":  # add more opening lines templates
                for j, t in enumerate(TEMP_FALSE_BELIEF_OPENING_LINES):
                    new_item = item_processed.copy()
                    text_lines[0] = t
                    new_item["text"] = "".join([l + "\n" for l in text_lines]).strip()
                    new_item["template"] = j + 1
                    output[sample_num] = new_item
                    sample_num += 1

    json_object = json.dumps(output, indent=4)

    output_file = output_file.with_stem(
        f"t_[1, 2, 3, 4, 5, 6, 7]_dm_full_wbias_{with_bias}"
    )
    print(f"Writing to {output_file}")
    with open(output_file, "w+") as outfile:
        outfile.write(json_object)
