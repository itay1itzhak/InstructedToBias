import argparse
import logging
from pathlib import Path
from templates import ALL_DECOY_PRODUCTS

from generate_samples_decoy import get_decoy_vals, Decoy_type
from generate_samples_certainty import get_certainty_vals, Certainty_type
from generate_false_belief import get_false_belief_vals, Belief_type
from samples_classes import SamplesGen, print_samples, write_samples_to_path


def get_values(args, product, bias_types_enums, with_bias) -> list[dict]:
    if args.bias_name == "decoy":
        return get_decoy_vals(args, product, bias_types_enums, with_bias)
    elif args.bias_name == "certainty":
        return get_certainty_vals(args, bias_types_enums, with_bias)
    elif args.bias_name == "false_belief":
        return get_false_belief_vals(args, bias_types_enums, with_bias)
    else:
        raise NameError(f"Not supported bias name {args.bias_name}")


def get_bias_types(bias_name, bias_types, with_bias):
    bias_types_enums = []
    if bias_name == "decoy":
        if bias_types == "only_two_options" or not with_bias:
            bias_types_enums = [Decoy_type.TWO_OPTIONS]
        else:
            for t in bias_types.split(","):
                if t == "R":
                    bias_types_enums.append(Decoy_type.R)
                if t == "RF":
                    bias_types_enums.append(Decoy_type.RF)
                if t == "F":
                    bias_types_enums.append(Decoy_type.F)
                if t == "R_EXTREAM":
                    bias_types_enums.append(Decoy_type.R_EXTREAM)
                if t == "all":
                    bias_types_enums = [
                        Decoy_type.R,
                        Decoy_type.RF,
                        Decoy_type.F,
                        Decoy_type.R_EXTREAM,
                    ]
                else:
                    raise NameError(
                        f"Bias type not supported for bias name - {bias_name}, bias type - {bias_types}"
                    )
        return bias_types_enums
    if bias_name == "certainty":
        for t in args.bias_types.split(","):
            if t == "three_probs":
                bias_types_enums.append(Certainty_type.DEVIDE_OPTION_A_TO_THREE_PROBS)
            elif t == "two_probs":
                bias_types_enums.append(Certainty_type.DEVIDE_OPTION_A_TO_TWO_PROBS)
            elif t == "not_probable":
                bias_types_enums.append(Certainty_type.NOT_PROBABLE)
            else:
                # raise a specific exception for when no bias type is given
                raise NameError(
                    f"Bias type not supported for bias name - {bias_name}, bias type - {bias_types}"
                )
        return bias_types_enums

    if bias_name == "false_belief":
        for t in bias_types.split(","):
            if t == "dm_1":
                bias_types_enums.append(Belief_type.EXP_DM_1)
            elif t == "dm_2":
                bias_types_enums.append(Belief_type.EXP_DM_2)
            elif t == "dm_full":
                raise NameError(
                    f"Bias type dm_full refers to the full data by DeepMind. We do not provide thier data, please refer to the paper authors for details on the data. https://arxiv.org/abs/2207.07051"
                )
            else:
                raise NameError(
                    f"Bias type not supported for bias name - {bias_name}, bias type - {bias_types}"
                )
        return bias_types_enums


def generate_all_samples(
    dest_path: Path,
    bias_name: str,
    bias_types: str,
    templates_str: str,
    with_bias: bool,
    product: str,
    all_options_permutations: bool,
    overwrite: bool,
    args: argparse.Namespace = None,
):
    bias_types_enums = get_bias_types(bias_name, bias_types, with_bias)
    templates = [int(t) for t in templates_str.split(",")]

    values = get_values(args, product, bias_types_enums, with_bias)

    gen = SamplesGen(
        bias_name, templates, values, bias_types_enums, with_bias=with_bias
    )

    samples = gen.generate_samples()
    print_samples(samples)
    write_samples_to_path(
        samples,
        dest_path,
        bias_name,
        bias_types,
        templates,
        with_bias,
        product,
        all_options_permutations,
        overwrite=overwrite,
    )


def run_main(args):
    logging.info(f"Creating samples for {args.bias_name}...")
    logging.info("=" * 80)

    if args.bias_name == "decoy":
        if args.product == "all":
            all_products = ALL_DECOY_PRODUCTS
        else:
            all_products = args.product.split(",")
    else:
        all_products = [""]

    for product in all_products:
        for with_bias in [True, False]:
            generate_all_samples(
                Path(args.dest_path),
                args.bias_name,
                args.bias_types,
                args.templates,
                with_bias,
                product,
                bool(args.all_options_permutations),
                overwrite=not args.do_not_overwrite,
                args=args,
            )

    logging.info("=" * 80)
    logging.info("All Done!")


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--dest_path", type=str, default="Data/", help="")
    parser.add_argument(
        "--templates",
        type=str,
        default="1,2,3,4,5",
        help="Which templates to use from the templates.py file.",
    )

    parser.add_argument(
        "--num_of_subtemplates",
        type=int,
        default=1000,
        help="How many templates in certainty.",
    )

    parser.add_argument(
        "--bias_name",
        type=str,
        default="decoy",
        help="Which bias to use from all biases: decoy, certainty, false_belief.",
    )

    parser.add_argument(
        "--bias_types",
        type=str,
        default="all",
        help="Types of bias. For decoy: only_two_options, or all.",
    )
    parser.add_argument(
        "--with_bias",
        default=False,
        action="store_true",
        help="Are the created samples should be with bias, or unbiased versions.",
    )
    parser.add_argument(
        "--do_not_overwrite",
        default=False,
        action="store_true",
        help="If set to true, samples with same names that already exist will not be overwritten.",
    )
    parser.add_argument(
        "--product",
        type=str,
        default="",
        help="For decoy bias only. Could be beer, car or phone.",
    )

    parser.add_argument(
        "--product_type",
        type=str,
        default="brand",
        help="For decoy bias only. Could be brand, options etc.",
    )

    parser.add_argument(
        "--all_options_permutations",
        type=str,
        default="True",
        help="If set to True, samples will be created with all possible permutaitons for options position.",
    )

    parser.add_argument(
        "--comments_to_file_name",
        type=str,
        default="",
        help="Any comments about this specific data creation, experiment type or something similar.",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()
    run_main(args)
