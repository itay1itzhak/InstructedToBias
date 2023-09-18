import itertools
import numpy as np

from samples_classes import *
from templates import *


def get_decoy_bias_third_option_vals(
    bias_type, vals, with_bias, price_diff="mean", quality_diff=10
):
    """
    :param bias_type: Decoy_type
    :param vals: list of values [price_1, price_2, quality_1, quality_2]
    :param with_bias: bool
    :param price_diff: "mean" or "extream"
    :param quality_diff: int
    :return: price_3, quality_3
    """
    # target price and quality
    p_2 = float(vals[1].replace("$", "").replace("K", ""))
    q_2 = int(vals[3])

    # possible decoy quality
    lower_quality_p2 = str(max(0, q_2 - quality_diff))
    higher_quality_p2 = str(max(0, q_2 + quality_diff))

    def get_decoy_vals():
        """
        :return: price_3, quality_3
        this function returns the price and quality of the biased decoy option
        """
        if price_diff == "mean":
            higher_p2 = p_2 + (0.25 * p_2)
            extreamly_higher_p2 = p_2 + (0.5 * p_2)
        else:
            raise Exception(f"Unvalid price_diff! Input price diff - {price_diff}")
        if "." in vals[0] or "." in vals[1]:
            higher_p2 = "$" + str(round(higher_p2)) + ".98"
            extreamly_higher_p2 = "$" + str(round(extreamly_higher_p2)) + ".98"
        else:
            higher_p2 = "$" + str(round(higher_p2))
            extreamly_higher_p2 = "$" + str(round(extreamly_higher_p2))

        if bias_type == Decoy_type.F:  # same price, worse quality
            return vals[1], lower_quality_p2
        elif bias_type == Decoy_type.R:  # higher price, same quality
            return higher_p2, str(q_2)
        elif bias_type == Decoy_type.R_EXTREAM:  # extream higher price, same quality
            return extreamly_higher_p2, str(q_2)
        elif bias_type == Decoy_type.RF:  # higher price, worse quality
            return higher_p2, lower_quality_p2
        else:
            raise Exception(f"Unvalid Decoy Type! Input bias type - {bias_type}")

    def get_non_decoy_vals():
        """
        :return: price_3, quality_3
        this function returns the price and quality of the non biased third option
        """
        if price_diff == "mean":
            lower_p2 = p_2 - (0.25 * p_2)
            extreamly_lower_p2 = p_2 - (0.5 * p_2)
        else:
            raise Exception(f"Unvalid price_diff! Input price diff - {price_diff}")

        if "." in vals[0] or "." in vals[1]:
            lower_p2 = "$" + str(round(lower_p2)) + ".98"
            extreamly_lower_p2 = "$" + str(round(extreamly_lower_p2)) + ".98"
        else:
            lower_p2 = "$" + str(round(lower_p2))
            extreamly_lower_p2 = "$" + str(round(extreamly_lower_p2))

        if bias_type == Decoy_type.F:  # same price as p_2, lower quality than p_1
            return vals[1], higher_quality_p2
        elif bias_type == Decoy_type.R:  # lower price, same quality
            return lower_p2, str(q_2)
        elif bias_type == Decoy_type.R_EXTREAM:  # lower price, better quality
            return lower_p2, higher_quality_p2
        elif bias_type == Decoy_type.RF:  # extream lower price, lower quality
            return extreamly_lower_p2, lower_quality_p2
        else:
            raise Exception(f"Unvalid Decoy Type! Input bias type - {bias_type}")

    # add a third option that will be a decoy
    if with_bias:
        return get_decoy_vals()
    # add a third option that will not be a decoy
    else:
        return get_non_decoy_vals()


def get_products_fixed_prices(product):
    """
    :param product: str
    :return: first_prices, second_prices
    this function returns the fixed prices ranges for the products
    """
    if product == "car":
        first_prices = list(range(5000, 10000, 1000))
        second_prices = list(range(15000, 39000, 5000))
    elif product == "car_cheaper":
        first_prices = list(range(15000, 39000, 5000))
        second_prices = list(range(5000, 10000, 1000))
    elif product == "phone_cheaper":
        first_prices = list(range(300, 951, 150))
        second_prices = list(range(100, 250, 30))
    elif product == "phone":
        first_prices = list(range(100, 250, 30))
        second_prices = list(range(300, 951, 150))
    elif product == "property":
        first_prices = list(range(80, 111, 10))  # [80, 90, 100, 110]
        second_prices = list(range(250, 421, 50))  # [250, 300, 350, 400]
    elif product == "property_cheaper":
        first_prices = list(range(250, 421, 50))  # [250, 300, 350, 400]
        second_prices = list(range(80, 111, 10))  # [80, 90, 100, 110]
    elif product == "frying_pan":
        first_prices = np.round(
            np.arange(9.99, 49.00, 10), 2
        ).tolist()  # [9.99, 19.99, 29.99, 39.99]
        second_prices = np.round(
            np.arange(59.99, 200.00, 40), 2
        ).tolist()  # [59.99, 99.99, 139.99, 179.99]
    elif product == "frying_pan_cheaper":
        first_prices = np.round(
            np.arange(59.99, 200.00, 40), 2
        ).tolist()  # [59.99, 99.99, 139.99, 179.99]
        second_prices = np.round(
            np.arange(9.99, 49.00, 10), 2
        ).tolist()  # [9.99, 19.99, 29.99, 39.99]

    else:
        raise Exception(f"Product {product} is not supported.")

    assert len(first_prices) == len(second_prices)
    return first_prices, second_prices


def get_decoy_quality_ratings(product):
    """
    this function returns the quality ratings for the decoy options
    """
    first_quality_ratings = list(range(40, 61, 10))
    second_quality_ratings = list(range(60, 81, 10))

    # wider gap for car
    if product == "car":
        first_quality_ratings = list(range(20, 41, 10))
        second_quality_ratings = list(range(60, 81, 10))
    # narrower gap for phone
    if product == "phone":
        first_quality_ratings = list(range(50, 71, 10))
        second_quality_ratings = list(range(60, 81, 10))

    # swap when cheaper and low quality products are the target
    if "cheaper" in product:
        first_quality_ratings = list(range(60, 81, 10))
        second_quality_ratings = list(range(40, 61, 10))

    assert len(first_quality_ratings) == len(second_quality_ratings)

    return first_quality_ratings, second_quality_ratings


def generate_values_decoy(product, with_bias, bias_types_enums):
    all_vals = ""
    first_prices, second_prices = get_products_fixed_prices(product)
    first_quality_ratings, second_quality_ratings = get_decoy_quality_ratings(product)

    vals_str = "".join(
        [
            str(first_prices),
            str(second_prices),
            str(first_quality_ratings),
            str(second_quality_ratings),
        ]
    )

    all_combinations = list(
        itertools.product(
            zip(first_prices, second_prices),
            zip(first_quality_ratings, second_quality_ratings),
        )
    )

    all_vals = [
        f"${prices[0]},${prices[1]},{qualities[0]},{qualities[1]},"
        for prices, qualities in all_combinations
    ]

    if bias_types_enums == [
        Decoy_type.TWO_OPTIONS
    ]:  # if there are only two options, no decoy, should choose cheap option
        all_vals = [s + "1" for s in all_vals]
    elif with_bias:  # decoy is in third option, might change that for other templates
        all_vals = [s + "2" for s in all_vals]
    else:  # third option will not be a valid decoy
        all_vals = [s + "3" for s in all_vals]

    return all_vals, vals_str


def get_all_prices_qualities(
    bias_type, vals, with_bias, product, all_options_permutations
):
    if bias_type == Decoy_type.TWO_OPTIONS:
        price_3 = -1
        quality_3 = -1
        name_3 = "no_decoy"
    else:
        price_3, quality_3 = get_decoy_bias_third_option_vals(
            bias_type, vals, with_bias
        )
        name_3 = "decoy"

    if "property" in product:  # change $100 to $100K for house property prices
        price_suffix = "K"
    else:
        price_suffix = ""

    all_prices_qualities = [
        (vals[0] + price_suffix, vals[2], "competitor"),
        (vals[1] + price_suffix, vals[3], "target"),
        (str(price_3) + price_suffix, quality_3, name_3),
    ]

    if all_options_permutations:
        if bias_type == Decoy_type.TWO_OPTIONS:
            # permute options 1 and 2, and keep 3 in the same place because it's a dummy option
            all_options = [
                list(x) + [all_prices_qualities[2]]
                for x in list(itertools.permutations(all_prices_qualities[:2]))
            ]
        else:
            all_options = list(itertools.permutations(all_prices_qualities))
    else:
        all_options = [all_prices_qualities]

    return all_options


def add_decoy_values_different_permutations(
    values,
    bias_type,
    with_bias,
    product,
    product_type,
    package,
    quality_measurment,
    vals,
    vals_str,
    all_options_permutations,
):
    all_options = get_all_prices_qualities(
        bias_type, vals, with_bias, product, all_options_permutations
    )
    for permut_id, cur_prices_qualities in enumerate(all_options):
        competitor_index = -1
        target_index = -1
        decoy_index = -1
        for i, p in enumerate(cur_prices_qualities):
            if p[2] == "competitor":
                competitor_index = i
            if p[2] == "target":
                target_index = i
            if p[2] == "decoy":
                decoy_index = i
        if with_bias:
            human_or_right_answer = target_index
        elif decoy_index == -1:  # there's no decoy, competitor is the other option
            human_or_right_answer = competitor_index
        else:
            human_or_right_answer = decoy_index

        values.append(
            {
                "product": product,
                "product_type": product_type,
                "package": package,
                "quality_measurment": quality_measurment,
                "price1": cur_prices_qualities[0][0],
                "price2": cur_prices_qualities[1][0],
                "quality1": cur_prices_qualities[0][1],
                "quality2": cur_prices_qualities[1][1],
                "price3": cur_prices_qualities[2][0],
                "quality3": cur_prices_qualities[2][1],
                "vals_range": vals_str,
                "bias_type": bias_type,
                "human_or_right_answer": human_or_right_answer + 1,
                "competitor": competitor_index + 1,
                "target": target_index + 1,
                "decoy": decoy_index + 1,
                "permutation_id": permut_id,
            }
        )

    return values


def get_products_texts(product):
    if "beer" in product:
        package = "sixpack"
        quality_measurment = (
            "the average quality rating made by subjects in a blind taste test"
        )
    elif "car" in product:
        package = "vehicle"
        quality_measurment = "the average riding quality rating made by car experts"
    elif "phone" in product:
        package = "device"
        quality_measurment = "the average quality rating made by phone experts"
    elif "hamburger" in product:
        package = "hamburger meal"
        quality_measurment = "the average taste rating made by food critics"
    elif "property" in product:
        package = "property"
        quality_measurment = "the average rating made by real estate experts"
    elif "frying pan" in product or "frying" in product:
        package = "frying pan"
        quality_measurment = "the average quality rating made by professional chefs"

    else:
        raise Exception(f"Non supported decoy product - {product}")

    return package, quality_measurment


def get_decoy_vals(args, product, bias_types_enums, with_bias):
    """
    :param args: args
    :param bias_types_enums: list of bias types
    :return: values
    returns the values for the decoy bias
    """
    values = []
    all_vals, vals_str = generate_values_decoy(product, with_bias, bias_types_enums)
    package, quality_measurment = get_products_texts(product)

    for vals in all_vals:
        vals = vals.split(",")
        for bias_type in bias_types_enums:
            add_decoy_values_different_permutations(
                values,
                bias_type,
                with_bias,
                product,
                args.product_type,
                package,
                quality_measurment,
                vals,
                vals_str,
                args.all_options_permutations,
            )

    return values
