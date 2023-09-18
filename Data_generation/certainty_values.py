def get_certainty_bias_three_options():
    all_gen_vals = {
        "first_probs": [33, 34, 35] + [20, 25, 25, 25],
        "second_probs": [66, 65, 64] + [79, 74, 74, 74],
        "third_probs": [1, 1, 1] + [1, 1, 1, 1],
        "first_prizes": list(range(2500, 3501, 500)) + [1000, 1000, 1500, 5000],
        "second_prizes": list(range(2400, 2601, 100)) + [800, 850, 1300, 4800],
        "third_prizes": [0] * 3 + [0, 0, 0, 0],
        "option_b_prize": list(range(2400, 2601, 100)) + [800, 850, 1300, 4800],
        "option_b_probe": [100] * 3 + [100, 100, 100, 100],
    }

    prizes = [
        all_gen_vals["first_prizes"],
        all_gen_vals["second_prizes"],
        all_gen_vals["third_prizes"],
        all_gen_vals["option_b_prize"],
    ]

    probs = [
        all_gen_vals["first_probs"],
        all_gen_vals["second_probs"],
        all_gen_vals["third_probs"],
        all_gen_vals["option_b_probe"],
    ]

    return all_gen_vals, prizes, probs


def get_certainty_not_bias_three_options():
    all_gen_vals = {
        "first_probs": [33, 34, 35] + [20, 25, 25, 25],
        "second_probs": [67, 66, 65] + [80, 75, 75, 75],
        "option_b_first_probs": [34, 35, 36] + [21, 26, 26, 26],
        "option_b_second_probs": [66, 65, 64] + [79, 74, 74, 74],
        "first_prizes": list(range(2500, 3501, 500)) + [1000, 1000, 1500, 5000],
        "second_prizes": [0] * 3 + [0, 0, 0, 0],
        "option_b_first_prizes": list(range(2400, 2601, 100)) + [800, 850, 1300, 4800],
        "option_b_second_prize": [0] * 3 + [0, 0, 0, 0],
    }

    prizes = [
        all_gen_vals["first_prizes"],
        all_gen_vals["second_prizes"],
        all_gen_vals["option_b_first_prizes"],
        all_gen_vals["option_b_second_prize"],
    ]
    probs = [
        all_gen_vals["first_probs"],
        all_gen_vals["second_probs"],
        all_gen_vals["option_b_first_probs"],
        all_gen_vals["option_b_second_probs"],
    ]

    return all_gen_vals, prizes, probs


def get_certainty_bias_two_options():
    all_gen_vals = {
        "first_probs": [80, 80, 80] + [85, 85, 70, 60],
        "second_probs": [20, 20, 20] + [15, 15, 30, 40],
        "first_prizes": [4000, 5000, 6000] + [5000, 6000, 3000, 2000],
        "second_prizes": [0] * 7,
        "option_b_prize": [3000, 3000, 4000, 4000, 5000, 2000, 1000],
        "option_b_probe": [100] * 7,
    }

    prizes = [
        all_gen_vals["first_prizes"],
        all_gen_vals["second_prizes"],
        all_gen_vals["option_b_prize"],
    ]

    probs = [
        all_gen_vals["first_probs"],
        all_gen_vals["second_probs"],
        all_gen_vals["option_b_probe"],
    ]
    return all_gen_vals, prizes, probs


def get_certainty_not_bias_two_options():
    all_gen_vals = {
        "first_probs": [20, 20, 20] + [25, 30, 20, 15],
        "second_probs": [80, 80, 80] + [75, 70, 80, 85],
        "option_b_first_probs": [25, 25, 25] + [30, 35, 25, 20],
        "option_b_second_probs": [75, 75, 75] + [70, 65, 75, 80],
        "first_prizes": [4000, 5000, 6000] + [5000, 6000, 3000, 2000],
        "second_prizes": [0] * 7,
        "option_b_first_prize": [3000, 3000, 4000] + [4000, 5000, 2000, 1000],
        "option_b_second_prize": [0] * 7,
    }

    prizes = [
        all_gen_vals["first_prizes"],
        all_gen_vals["second_prizes"],
        all_gen_vals["option_b_first_prize"],
        all_gen_vals["option_b_second_prize"],
    ]
    probs = [
        all_gen_vals["first_probs"],
        all_gen_vals["second_probs"],
        all_gen_vals["option_b_first_probs"],
        all_gen_vals["option_b_second_probs"],
    ]
    return all_gen_vals, prizes, probs


def get_certainty_bias_not_probable_options():
    all_gen_vals = {
        "first_probs": [45, 40, 30, 25, 20, 15, 10],
        "second_probs": [55, 60, 70, 75, 80, 85, 90],
        "option_b_first_probs": [90, 80, 60, 50, 40, 30, 20],
        "option_b_second_probs": [10, 20, 40, 50, 60, 70, 80],
        "first_prizes": [6000, 7000, 8000, 9000, 10000, 11000, 12000],
        "second_prizes": [0] * 7,
        "option_b_first_prize": [3000, 3500, 4000, 4500, 5000, 5500, 6000],
        "option_b_second_prize": [0] * 7,
    }

    prizes = [
        all_gen_vals["first_prizes"],
        all_gen_vals["second_prizes"],
        all_gen_vals["option_b_first_prize"],
        all_gen_vals["option_b_second_prize"],
    ]
    probs = [
        all_gen_vals["first_probs"],
        all_gen_vals["second_probs"],
        all_gen_vals["option_b_first_probs"],
        all_gen_vals["option_b_second_probs"],
    ]
    return all_gen_vals, prizes, probs


def get_certainty_not_bias_not_probable_options():
    all_gen_vals = {
        "first_probs": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
        "second_probs": [99.9, 99.8, 99.7, 99.6, 99.5, 99.4, 99.3],
        "option_b_first_probs": [0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4],
        "option_b_second_probs": [99.8, 99.6, 99.4, 99.2, 99, 98.8, 98.6],
        "first_prizes": [6000, 7000, 8000, 9000, 10000, 11000, 12000],
        "second_prizes": [0] * 7,
        "option_b_first_prize": [3000, 3500, 4000, 4500, 5000, 5500, 6000],
        "option_b_second_prize": [0] * 7,
    }

    prizes = [
        all_gen_vals["first_prizes"],
        all_gen_vals["second_prizes"],
        all_gen_vals["option_b_first_prize"],
        all_gen_vals["option_b_second_prize"],
    ]
    probs = [
        all_gen_vals["first_probs"],
        all_gen_vals["second_probs"],
        all_gen_vals["option_b_first_probs"],
        all_gen_vals["option_b_second_probs"],
    ]
    return all_gen_vals, prizes, probs
