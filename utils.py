from pathlib import Path
import os


INSTURCT_MODELS = [
    "text-davinci-002",
    "text-davinci-003",
    "gpt-4-0314",
    "flan-t5-small",
    "flan-t5-base",
    "flan-t5-large",
    "flan-t5-xl",
    "flan-t5-xxl",
]
VANILLA_MODELS = [
    "davinci",
    "t5-xl",
    "t5-3b",
    "t5-v1_1-xl",
    "t5-v1_1-xxl",
    "llama_7B",
    "llama_13B",
    "llama-7b",
    "llama-13b",
]

OPENAI_MODELS = [
    "gpt-4-0314",
    "gpt-4",
    "text-davinci-003",
    "text-davinci-002",
    "text-davinci-001",
    "davinci",
    "curie",
    "babbage",
]

T5_MODELS = [
    "t5-xl",
    "t5-3b",
    "t5-v1_1-small",
    "t5-v1_1-base",
    "t5-v1_1-large",
    "t5-v1_1-xl",
    "t5-v1_1-xxl",
]

FLAN_T5_MODELS = [
    "flan-t5-small",
    "flan-t5-base",
    "flan-t5-large",
    "flan-t5-xl",
    "flan-t5-xxl",
]


def get_map_model_names():
    return {
        "davinci": "DaVinci",
        "text-davinci-002": "DaVinci-002",
        "text-davinci-003": "DaVinci-003",
        "gpt-4-0314": "GPT-4",
        "gpt-4": "GPT-4",
        "text-davinci-001": "DaVinci-001",
        "t5-v1_1-small": "T5-Small",
        "t5-v1_1-base": "T5-Base",
        "t5-v1_1-large": "T5-Large",
        "t5-v1_1-xl": "T5-XL",
        "t5-v1_1-xxl": "T5-XXL",
        "flan-t5-small": "Flan-T5-Small",
        "flan-t5-base": "Flan-T5-Base",
        "flan-t5-large": "Flan-T5-Large",
        "flan-t5-xl": "Flan-T5-XL",
        "flan-t5-xxl": "Flan-T5-XXL",
    }


def get_data_dir(
    base_path: Path, bias_name: str, all_options_permutations: bool, product: str
):
    if all_options_permutations:
        permute = "all_permutations"
    else:
        permute = "no_permutations"

    if bias_name == "decoy":
        data_dir_name = base_path.joinpath(bias_name, product, permute)
    else:
        data_dir_name = base_path.joinpath(bias_name, permute)

    os.makedirs(data_dir_name, exist_ok=True)

    return data_dir_name


def get_data_dir_and_file_name(
    base_path: Path,
    bias_name: str,
    bias_types: str,
    templates: list[int],
    with_bias: bool,
    product: str,
    all_options_permutations: bool,
    comments_to_file_name="",
):
    data_dir_name = get_data_dir(
        base_path, bias_name, all_options_permutations, product
    )

    if with_bias:
        with_bias = "Treatment"
    else:
        with_bias = "Control"

    data_file_name = Path(
        f"{comments_to_file_name}t_{templates}_{bias_types}_{with_bias}.json"
    )

    return data_dir_name, data_file_name


def get_prediction_dir_name(
    predictions_dir,
    data_path,
    engine,
    predict_according_to_log_probs,
    should_normalize,
    with_format_few_shot,
    with_task_few_shot,
    k_shot,
    comments_to_file_name="",
):
    if predict_according_to_log_probs:
        log_probs_dir = "max_prob_pred"
    else:
        log_probs_dir = "gen_pred"
    if should_normalize:
        is_normalize = "_normalized"
    else:
        is_normalize = ""
    # if not with_format_few_shot and not with_task_few_shot:
    #     k_shot = 0

    # keep the inner dir stcuture of the data for the prediction dir
    predictions_dir = predictions_dir.joinpath(*data_path.parts[1:])

    # add the prediction dir stracture
    predictions_dir_final = predictions_dir.joinpath(
        # bias_name,
        engine,
        f"few_shot_{k_shot}",
        log_probs_dir + is_normalize,
        f"format_{with_format_few_shot}_task_{with_task_few_shot}",
    )

    if not os.path.exists(predictions_dir_final):
        # create the dir if not exists with no error
        os.makedirs(predictions_dir_final, exist_ok=True)

    return predictions_dir_final


def get_across_exp_result_file_prefix(
    bias_name,
    all_options_permutations,
    product,
    pred_dir,
    engine,
    predict_according_to_log_probs,
    normalize_log_prob,
    with_format_few_shot,
    with_task_few_shot,
    k_shot,
    templates,
):
    data_dir = get_data_dir(
        Path("Data/"),
        bias_name,
        all_options_permutations,
        product,
    )
    full_pred_dir = get_prediction_dir_name(
        pred_dir,
        data_dir,
        engine,
        predict_according_to_log_probs,
        normalize_log_prob,
        with_format_few_shot,
        with_task_few_shot,
        k_shot,
    )
    pred_file_name = f"t_{templates}"
    file_prefix = full_pred_dir.joinpath(pred_file_name)

    return file_prefix


def get_prediction_output_files_names(
    predictions_dir,
    data_path,
    bias_name,
    engine,
    predict_according_to_log_probs,
    should_normalize,
    with_format_few_shot,
    with_task_few_shot,
    k_shot: int,
    bias_types,
    templates,
    with_bias,
    product,
    all_options_permutations,
):
    if data_path != Path("Data/"):
        data_dir = Path(os.path.dirname(data_path))
        data_file = Path(os.path.basename(data_path))
    else:
        data_dir, data_file = get_data_dir_and_file_name(
            Path("Data/"),
            bias_name,
            bias_types,
            templates,
            with_bias,
            product,
            all_options_permutations,
        )

    predictions_dir = get_prediction_dir_name(
        predictions_dir,
        data_dir,
        engine,
        predict_according_to_log_probs,
        should_normalize,
        with_format_few_shot,
        with_task_few_shot,
        k_shot,
    )

    output_path = predictions_dir.joinpath(data_file).with_suffix(".json")

    output_with_metadata_path = output_path.with_stem(
        f"{output_path.stem}_with_metadata"
    )

    os.makedirs(predictions_dir, exist_ok=True)

    return output_path, output_with_metadata_path


def get_results_comments_name(conditions, templates, bias_types):
    cond_string = (
        str(conditions)
        .replace("'", "")
        .replace("{", "")
        .replace("}", "")
        .replace(":", "")
        .replace("Certainty_type.", "")
        .replace("Decoy_type.", "")
        .replace(" ", "_")
        .replace(".", "_")
    )
    if len(cond_string) > 30:  # 300
        cond_string = "long_"  # "bias_types_3_"  #   # "R_EXTREAM"

    return f"_{str(templates)}_{bias_types}_" + cond_string


def get_bias_type_templates_defaults(bias_name, bias_types, templates):
    if templates is None:
        if bias_name == "decoy":
            templates = "[1, 2, 3, 4]"
        elif bias_name == "certainty":
            templates = "[1, 2, 3]"
        elif bias_name == "false_belief":
            templates = "[1, 2, 3, 4, 5, 6, 7]"

    if bias_types is None:
        if bias_name == "decoy":
            bias_types = "all"
        elif bias_name == "certainty":
            bias_types = "three_probs,two_probs"
        elif bias_name == "false_belief":
            # bias_types = "dm_1,dm_2"
            bias_types = "dm_full"

    return bias_types, templates
