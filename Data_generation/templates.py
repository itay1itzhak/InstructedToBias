from string import Template

######################################################## Decoy #############################################

# With three options
TEMP_DECOY_THREE_OPTIONS_1 = Template(
    "Below you will find three $PRODUCT $PRODUCT_TYPEs.\n"
    + "You know only the price per $PACKAGE and $QUALITY_MEASURE (100 = best, 0 = worst).\n"
    + "Given that you had to choose one $PRODUCT_TYPE to buy on this information alone, which one would it be?\n"
    + "$PRODUCT_TYPE_UPPERCASE 1 - price is $PRICE1, quality rating is $QUALITY1.\n"
    + "$PRODUCT_TYPE_UPPERCASE 2 - price is $PRICE2, quality rating is $QUALITY2.\n"
    + "$PRODUCT_TYPE_UPPERCASE 3 - price is $PRICE3, quality rating is $QUALITY3.\n"
    + "Answer:"
)


TEMP_DECOY_THREE_OPTIONS_2 = Template(
    "Below you will find three $PRODUCT $PRODUCT_TYPEs.\n"
    + "You know only the price per $PACKAGE and $QUALITY_MEASURE (100 = best, 0 = worst).\n"
    + "$PRODUCT_TYPE_UPPERCASE 1 - price is $PRICE1, quality rating is $QUALITY1.\n"
    + "$PRODUCT_TYPE_UPPERCASE 2 - price is $PRICE2, quality rating is $QUALITY2.\n"
    + "$PRODUCT_TYPE_UPPERCASE 3 - price is $PRICE3, quality rating is $QUALITY3.\n"
    + "Given that you had to choose one $PRODUCT_TYPE to buy on this information alone, which one would it be?\n"
    + "Answer:"
)

TEMP_DECOY_THREE_OPTIONS_3 = Template(
    "The following are three $PRODUCT $PRODUCT_TYPEs.\n"
    + "The only details you know are the price per $PACKAGE and $QUALITY_MEASURE (100 = best, 0 = awful).\n"
    + "$PRODUCT_TYPE_UPPERCASE 1 - price is $PRICE1, and the quality rating is $QUALITY1.\n"
    + "$PRODUCT_TYPE_UPPERCASE 2 - price is $PRICE2, and the quality rating is $QUALITY2.\n"
    + "$PRODUCT_TYPE_UPPERCASE 3 - price is $PRICE3, and the quality rating is $QUALITY3.\n"
    + "In the event that you had to make a decision based solely on the information presented here, which would be the $PRODUCT_TYPE you would buy?\n"
    + "Answer:"
)

TEMP_DECOY_THREE_OPTIONS_4 = Template(
    "Here are three $PRODUCT $PRODUCT_TYPEs.\n"
    + "The only details you know are the price per $PACKAGE and $QUALITY_MEASURE (100 = best, 0 = awful).\n"
    + "In the event that you had to make a decision based solely on the information presented here, which would be the $PRODUCT_TYPE you would buy?\n"
    + "$PRODUCT_TYPE_UPPERCASE 1 - price is $PRICE1, and the quality rating is $QUALITY1.\n"
    + "$PRODUCT_TYPE_UPPERCASE 2 - price is $PRICE2, and the quality rating is $QUALITY2.\n"
    + "$PRODUCT_TYPE_UPPERCASE 3 - price is $PRICE3, and the quality rating is $QUALITY3.\n"
    + "The $PRODUCT_TYPE I would choose would be:\n"
    + "Answer:"
)

TEMP_DECOY_THREE_OPTIONS_5 = Template(
    "The following are three $PRODUCT $PRODUCT_TYPEs.\n"
    + "The only details you know are the price per $PACKAGE and $QUALITY_MEASURE (100 = best, 0 = awful).\n"
    + "$PRODUCT_TYPE_UPPERCASE 1 - price is $PRICE1, and the quality rating is $QUALITY1.\n"
    + "$PRODUCT_TYPE_UPPERCASE 2 - price is $PRICE2, and the quality rating is $QUALITY2.\n"
    + "$PRODUCT_TYPE_UPPERCASE 3 - price is $PRICE3, and the quality rating is $QUALITY3.\n"
    + "In the event that you had to make a decision based solely on the information presented here, which would be the $PRODUCT_TYPE you would buy?\n"
    + "Answer:"
)

ALL_DECOY_TEMP_THREE_OPTIONS = {
    1: TEMP_DECOY_THREE_OPTIONS_1,
    2: TEMP_DECOY_THREE_OPTIONS_2,
    3: TEMP_DECOY_THREE_OPTIONS_3,
    4: TEMP_DECOY_THREE_OPTIONS_4,
    5: TEMP_DECOY_THREE_OPTIONS_5,
}

# With Two options

TEMP_DECOY_TWO_OPTIONS_1 = Template(
    "Below you will find two $PRODUCT $PRODUCT_TYPEs.\n"
    + "You know only the price per $PACKAGE and $QUALITY_MEASURE (100 = best, 0 = worst).\n"
    + "Given that you had to choose one $PRODUCT_TYPE to buy on this information alone, which one would it be?\n"
    + "$PRODUCT_TYPE_UPPERCASE 1 - price is $PRICE1, quality rating is $QUALITY1.\n"
    + "$PRODUCT_TYPE_UPPERCASE 2 - price is $PRICE2, quality rating is $QUALITY2.\n"
    + "Answer:"
)


TEMP_DECOY_TWO_OPTIONS_2 = Template(
    "Below you will find two $PRODUCT $PRODUCT_TYPEs.\n"
    + "You know only the price per $PACKAGE and $QUALITY_MEASURE (100 = best, 0 = worst).\n"
    + "$PRODUCT_TYPE_UPPERCASE 1 - price is $PRICE1, quality rating is $QUALITY1.\n"
    + "$PRODUCT_TYPE_UPPERCASE 2 - price is $PRICE2, quality rating is $QUALITY2.\n"
    + "Given that you had to choose one $PRODUCT_TYPE to buy on this information alone, which one would it be?\n"
    + "Answer:"
)

TEMP_DECOY_TWO_OPTIONS_3 = Template(
    "The following are two $PRODUCT $PRODUCT_TYPEs.\n"
    + "The only details you know are the price per $PACKAGE and $QUALITY_MEASURE (100 = best, 0 = awful).\n"
    + "$PRODUCT_TYPE_UPPERCASE 1 - price is $PRICE1, and the quality rating is $QUALITY1.\n"
    + "$PRODUCT_TYPE_UPPERCASE 2 - price is $PRICE2, and the quality rating is $QUALITY2.\n"
    + "In the event that you had to make a decision based solely on the information presented here, which would be the $PRODUCT_TYPE you would buy?\n"
    + "Answer:"
)

TEMP_DECOY_TWO_OPTIONS_4 = Template(
    "Here are two $PRODUCT $PRODUCT_TYPEs.\n"
    + "The only details you know are the price per $PACKAGE and $QUALITY_MEASURE (100 = best, 0 = awful).\n"
    + "In the event that you had to make a decision based solely on the information presented here, which would be the $PRODUCT_TYPE you would buy?\n"
    + "$PRODUCT_TYPE_UPPERCASE 1 - price is $PRICE1, and the quality rating is $QUALITY1.\n"
    + "$PRODUCT_TYPE_UPPERCASE 2 - price is $PRICE2, and the quality rating is $QUALITY2.\n"
    + "The $PRODUCT_TYPE I would choose would be:\n"
    + "Answer:"
)

TEMP_DECOY_TWO_OPTIONS_5 = Template(
    "The following are two $PRODUCT $PRODUCT_TYPEs.\n"
    + "The only details you know are the price per $PACKAGE and $QUALITY_MEASURE (100 = best, 0 = awful).\n"
    + "$PRODUCT_TYPE_UPPERCASE 1 - price is $PRICE1, and the quality rating is $QUALITY1.\n"
    + "$PRODUCT_TYPE_UPPERCASE 2 - price is $PRICE2, and the quality rating is $QUALITY2.\n"
    + "Which option would you choose?\n"
    + "Answer:"
)

ALL_DECOY_TEMP_TWO_OPTIONS = {
    1: TEMP_DECOY_TWO_OPTIONS_1,
    2: TEMP_DECOY_TWO_OPTIONS_2,
    3: TEMP_DECOY_TWO_OPTIONS_3,
    4: TEMP_DECOY_TWO_OPTIONS_4,
    5: TEMP_DECOY_TWO_OPTIONS_5,
}

# Decoy few shot templates
# With two options

FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_1_OLD = Template(
    "The following are two table brands.\n"
    + "The only details you know are the tables colors.\n"
    + "Brand 1 - white.\n"
    + "Brand 2 - black.\n"
    + "The color I would choose would be:\n"
    + "Answer: Brand $OPTION."
)


FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_2_OLD = Template(
    "Here are two fruit brands.\n"
    + "You only need to choose one option of them.\n"
    + "Brand 1 - bananas.\n"
    + "Brand 2 - oranges.\n"
    + "Which option would you choose?\n"
    + "Answer: Brand $OPTION."
)

FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_3_OLD = Template(
    "Here are two shirt brands.\n"
    + "You only need to choose one option of them.\n"
    + "Brand 1 - white shirt.\n"
    + "Brand 2 - blue shirt.\n"
    + "Which option would you choose?\n"
    + "Answer: Brand $OPTION."
)

FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_4_OLD = Template(
    "Here are two pizza brands.\n"
    + "You only need to choose one option of them.\n"
    + "Brand 1 - city pizza.\n"
    + "Brand 2 - urban pizza.\n"
    + "Which option would you choose?\n"
    + "Answer: Brand $OPTION."
)

FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_5_OLD = Template(
    "Here are two shoes brands.\n"
    + "You only need to choose one option of them.\n"
    + "Brand 1 - sport shoes.\n"
    + "Brand 2 - running shoes.\n"
    + "Which option would you choose?\n"
    + "Answer: Brand $OPTION."
)

DECOY_FEW_SHOT_ANSWER = Template(" Brand $OPTION.")
FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_1 = {
    "question": "The following are two table brands.\n"
    + "The only details you know are the tables colors.\n"
    + "Brand 1 - white.\n"
    + "Brand 2 - black.\n"
    + "The color I would choose would be:\n"
    + "Answer:",
    "answer": DECOY_FEW_SHOT_ANSWER,
}

FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_2 = {
    "question": "Here are two fruit brands.\n"
    + "You only need to choose one option of them.\n"
    + "Brand 1 - bananas.\n"
    + "Brand 2 - oranges.\n"
    + "Which option would you choose?\n"
    + "Answer:",
    "answer": DECOY_FEW_SHOT_ANSWER,
}

FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_3 = {
    "question": "Here are two shirt brands.\n"
    + "You only need to choose one option of them.\n"
    + "Brand 1 - white shirt.\n"
    + "Brand 2 - blue shirt.\n"
    + "Which option would you choose?\n"
    + "Answer:",
    "answer": DECOY_FEW_SHOT_ANSWER,
}

FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_4 = {
    "question": "Here are two pizza brands.\n"
    + "You only need to choose one option of them.\n"
    + "Brand 1 - city pizza.\n"
    + "Brand 2 - urban pizza.\n"
    + "Which option would you choose?\n"
    + "Answer:",
    "answer": DECOY_FEW_SHOT_ANSWER,
}


FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_5 = {
    "question": "Here are two shoes brands.\n"
    + "You only need to choose one option of them.\n"
    + "Brand 1 - sport shoes.\n"
    + "Brand 2 - running shoes.\n"
    + "Which option would you choose?\n"
    + "Answer:",
    "answer": DECOY_FEW_SHOT_ANSWER,
}


ALL_DECOY_TWO_OPTIONS_FORMAT_FEW_SHOT = {
    # 1: FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_1_OLD,
    # 2: FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_2_OLD,
    # 3: FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_3_OLD,
    # 4: FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_4_OLD,
    # 5: FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_5_OLD,
    1: FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_1,
    2: FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_2,
    3: FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_3,
    4: FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_4,
    5: FORMAT_FEW_SHOT_TEXT_DECOY_TWO_OPTIONS_5,
}

# With three options

FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_1_OLD = Template(
    "The following are three table brands.\n"
    + "The only details you know are the tables' colors.\n"
    + "Brand 1 - white.\n"
    + "Brand 2 - black.\n"
    + "Brand 3 - brown.\n"
    + "The color I would choose would be:\n"
    + "Answer: Brand $OPTION."
)

FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_1 = {
    "question": "The following are three table brands.\n"
    + "The only details you know are the tables' colors.\n"
    + "Brand 1 - white.\n"
    + "Brand 2 - black.\n"
    + "Brand 3 - brown.\n"
    + "The color I would choose would be:\n"
    + "Answer:",
    "answer": DECOY_FEW_SHOT_ANSWER,
}


FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_2_OLD = Template(
    "Here are three fruit brands.\n"
    + "You only need to choose one option of them.\n"
    + "Brand 1 - bananas.\n"
    + "Brand 2 - oranges.\n"
    + "Brand 3 - apples.\n"
    + "Which option would you choose?\n"
    + "Answer: Brand $OPTION."
)

FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_2 = {
    "question": "Here are three fruit brands.\n"
    + "You only need to choose one option of them.\n"
    + "Brand 1 - bananas.\n"
    + "Brand 2 - oranges.\n"
    + "Brand 3 - apples.\n"
    + "Which option would you choose?\n"
    + "Answer:",
    "answer": DECOY_FEW_SHOT_ANSWER,
}

FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_3 = {
    "question": "Here are three shirt brands.\n"
    + "You only need to choose one option of them.\n"
    + "Brand 1 - black shirt.\n"
    + "Brand 2 - white shirt.\n"
    + "Brand 3 - blue shirt.\n"
    + "Which option would you choose?\n"
    + "Answer:",
    "answer": DECOY_FEW_SHOT_ANSWER,
}

FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_3_OLD = Template(
    "Here are three shirt brands.\n"
    + "You only need to choose one option of them.\n"
    + "Brand 1 - black shirt.\n"
    + "Brand 2 - white shirt.\n"
    + "Brand 3 - blue shirt.\n"
    + "Which option would you choose?\n"
    + "Answer: Brand $OPTION."
)

FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_4 = {
    "question": "Here are two pizza brands.\n"
    + "You only need to choose one option of them.\n"
    + "Brand 1 - city pizza.\n"
    + "Brand 2 - urban pizza.\n"
    + "Brand 3 - town pizza.\n"
    + "Which option would you choose?\n"
    + "Answer:",
    "answer": DECOY_FEW_SHOT_ANSWER,
}

FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_4_OLD = Template(
    "Here are two pizza brands.\n"
    + "You only need to choose one option of them.\n"
    + "Brand 1 - city pizza.\n"
    + "Brand 2 - urban pizza.\n"
    + "Brand 3 - town pizza.\n"
    + "Which option would you choose?\n"
    + "Answer: Brand $OPTION."
)

FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_5 = {
    "question": "Here are two shoes brands.\n"
    + "You only need to choose one option of them.\n"
    + "Brand 1 - sport shoes.\n"
    + "Brand 2 - running shoes.\n"
    + "Brand 3 - jogging shoes.\n"
    + "Which option would you choose?\n"
    + "Answer:",
    "answer": DECOY_FEW_SHOT_ANSWER,
}


FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_5_OLD = Template(
    "Here are two shoes brands.\n"
    + "You only need to choose one option of them.\n"
    + "Brand 1 - sport shoes.\n"
    + "Brand 2 - running shoes.\n"
    + "Brand 3 - jogging shoes.\n"
    + "Which option would you choose?\n"
    + "Answer: Brand $OPTION."
)


ALL_DECOY_THREE_OPTIONS_FORMAT_FEW_SHOT = {
    # 1: FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_1_OLD,
    # 2: FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_2_OLD,
    # 3: FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_3_OLD,
    # 4: FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_4_OLD,
    # 5: FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_5_OLD,
    1: FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_1,
    2: FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_2,
    3: FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_3,
    4: FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_4,
    5: FORMAT_FEW_SHOT_TEXT_DECOY_THREE_OPTIONS_5,
}

ALL_EXPENSIVE_DECOY_PRODUCTS = [
    "frying_pan",
    "car",
    "phone",
    "property",
]

ALL_CHEAP_DECOY_PRODUCTS = [
    "frying_pan_cheaper",
    "car_cheaper",
    "phone_cheaper",
    "property_cheaper",
]

ALL_DECOY_PRODUCTS = ALL_EXPENSIVE_DECOY_PRODUCTS + ALL_CHEAP_DECOY_PRODUCTS

######################################################## Certainty #############################################

CERTAINTY_TEMPLATES = {
    "ALL_OPTIONS_TEXT_CERTAINTY": {1: ("Option A", "Option B")},
    "OPTION_UNBIAS_CERTAINTY_THREE": {
        1: Template(
            "$PRIZE1 with a $PROB1 chance, $PRIZE2 with a $PROB2 chance, $PRIZE3 with a $PROB3 chance"
        ),
        2: Template(
            "$PROB1 to win $PRIZE1, $PROB2 to win $PRIZE2, $PROB3 to win $PRIZE3"
        ),
    },
    "OPTION_UNBIAS_CERTAINTY_TWO": {
        1: Template("$PRIZE1 with a $PROB1 chance, $PRIZE2 with a $PROB2 chance"),
        2: Template("$PROB1 to win $PRIZE1, $PROB2 to win $PRIZE2"),
    },
    "OPTION_UNBIAS_CERTAINTY_ONE": {
        1: Template("$PRIZE1 with probability $PROB1"),
        2: Template("$PROB1 to win $PRIZE1"),
    },
    "OPTION_BIAS_CERTAINTY_ONE": {
        1: Template("$PRIZE1 with certainty"),
        2: Template("$PRIZE1 for sure"),
        3: Template("100% to win $PRIZE1"),
    },
    "CERTAINTY_BIAS_MEGA": {
        1: Template(
            "Choose between:\n"
            + "$FIRST_OPTION_OPENING - $FIRST_OPTION.\n"
            + "$SECOND_OPTION_OPENING - $SECOND_OPTION.\n"
            + "What is your choice?\nAnswer:"
        ),
        2: Template(
            "Below you will find two options for getting a prize.\n"
            + "$FIRST_OPTION_OPENING - $FIRST_OPTION.\n"
            + "$SECOND_OPTION_OPENING - $SECOND_OPTION.\n"
            + "Given that these are the only options, which one would you choose?\nAnswer:"
        ),
        3: Template(
            "Which of the following would you prefer?\n"
            + "$FIRST_OPTION_OPENING - $FIRST_OPTION.\n"
            + "$SECOND_OPTION_OPENING - $SECOND_OPTION.\n"
            + "Answer:"
        ),
    },
    "ALL_CERTAINTY_FORMAT_FEW_SHOT_OBJECTS": {
        1: ["white table", "brown table"],
        2: ["bananas", "oranges"],
        3: ["white shirt", "black shirt"],
        4: ["pizza", "hamburger"],
        5: ["football", "basketball"],
    },
    "CERTAINTY_UNDECIDED_ANSWERS": [
        "t depends on the individual",
        "t depends on the situation",
    ],
}


######################################################## False Belife #############################################

TEMP_FALSE_BELIEF_SYLLOGISM_ALL_ARE = Template("All $X are $Y")

TEMP_FALSE_BELIEF_SYLLOGISM_SOME_ARE = Template("Some $X are $Y")

TEMP_FALSE_BELIEF_SYLLOGISM_NOT_ALL = Template("No $X are $Y")

TEMP_FALSE_BELIEF_SYLLOGISM_SOME_NOT = Template("Some $X are not $Y")

ALL_FALSE_BELIEF_SYLLOGISM = {
    "all_x_are_y": TEMP_FALSE_BELIEF_SYLLOGISM_ALL_ARE,
    "some_x_are_y": TEMP_FALSE_BELIEF_SYLLOGISM_SOME_ARE,
    "no_x_are_y": TEMP_FALSE_BELIEF_SYLLOGISM_NOT_ALL,
    "some_x_arent_y": TEMP_FALSE_BELIEF_SYLLOGISM_SOME_NOT,
}

TEMP_FALSE_BELIEF_OPENING_LINES = [
    "Determine if the following argument is logically valid -\n",
    "Determine if the following Conclusion stems from premise 1 and premise 2-\n",
    "Determine if the following Conclusion stems from premise 1 and premise 2, regardless of other world knowledge -\n",
    "This is an experiment to test people's reasoning ability. You will be given "
    + "premises to read and a certain conclusion that may be logically deduced from it. You should answer this question "
    + "on the assumption that all the information given in the premises "
    + "is, in fact, true. If you judge that the conclusion necessarily "
    + "follows from the statements in the passage, you should answer "
    + "'yes', otherwise 'no'.\n",
]


TEMP_FALSE_BELIEF_DEEPMIND_1 = Template(
    TEMP_FALSE_BELIEF_OPENING_LINES[0]
    + "\n"
    + "$PREMISE1.\n"
    + "$PREMISE2.\n"
    + "Conclusion: $CONCLUSION.\n"
    + "$CLOSING_LINE"
)

TEMP_FALSE_BELIEF_DEEPMIND_2 = Template(
    TEMP_FALSE_BELIEF_OPENING_LINES[1]
    + "\n"
    + "$PREMISE1.\n"
    + "$PREMISE2.\n"
    + "Conclusion: $CONCLUSION.\n"
    + "$CLOSING_LINE"
)

TEMP_FALSE_BELIEF_DEEPMIND_3 = Template(
    TEMP_FALSE_BELIEF_OPENING_LINES[2]
    + "\n"
    + "$PREMISE1.\n"
    + "$PREMISE2.\n"
    + "Conclusion: $CONCLUSION.\n"
    + "$CLOSING_LINE"
)

TEMP_FALSE_BELIEF_DEEPMIND_4 = Template(
    TEMP_FALSE_BELIEF_OPENING_LINES[3]
    + "\n"
    + "$PREMISE1.\n"
    + "$PREMISE2.\n"
    + "Conclusion: $CONCLUSION.\n"
    + "$CLOSING_LINE"
)

TEMP_FALSE_BELIEF_DEEPMIND_5 = Template(
    "Argument:\n"
    + "$PREMISE1.\n"
    + "$PREMISE2.\n"
    + "Conclusion: $CONCLUSION.\n"
    + "$CLOSING_LINE"
)

TEMP_FALSE_BELIEF_DEEPMIND_6 = Template(
    "Answer these logic problems carefully, by determining whether each argument is valid or invalid.\n\nArgument:\n"
    + "$PREMISE1.\n"
    + "$PREMISE2.\n"
    + "Conclusion: $CONCLUSION.\n"
    + "$CLOSING_LINE"
)

TEMP_FALSE_BELIEF_DEEPMIND_7 = Template(
    "Carefully evaluate these logical arguments, and determine whether each is valid or invalid.\n\nArgument:\n"
    + "$PREMISE1.\n"
    + "$PREMISE2.\n"
    + "Conclusion: $CONCLUSION.\n"
    + "$CLOSING_LINE"
)

ALL_FALSE_BELIEF_DEEPMIND_TEMP = {
    1: TEMP_FALSE_BELIEF_DEEPMIND_1,
    2: TEMP_FALSE_BELIEF_DEEPMIND_2,
    3: TEMP_FALSE_BELIEF_DEEPMIND_3,
    4: TEMP_FALSE_BELIEF_DEEPMIND_4,
    5: TEMP_FALSE_BELIEF_DEEPMIND_5,
    6: TEMP_FALSE_BELIEF_DEEPMIND_6,
    7: TEMP_FALSE_BELIEF_DEEPMIND_7,
}

ALL_FB_CLOSING_LINES = {
    1: "Answer:",
    2: "Is this argument logically valid?\nAnswer:",
}

FB_UNDECIDED_ANSWERS = [
    "t's not possible to",
    "t's impossible to say",
    "cannot be definitively",
    "cannot be drawn",
    "cannot be determined",
    "Please select one of the options from the table above",  # llama-2-chat common answer
]

FB_MORE_THAN_ONE_TOKEN_ANSWERS = {
    "is logically valid": True,
    "does logically follow": True,
    "is not logically valid": True,
    "does not logically follow": False,
}
# False Belife values
ALL_FB_OBJECTS_BIAS_DM_1 = {
    1: {
        "A": "flowers",
        "B": "animals",
        "C": "reptiles",
        "B_Obj": "animals",
    },
    2: {
        "A": "buildings",
        "B": "things that move",
        "C": "vehicles",
        "B_Obj": "things that move",
    },
}
ALL_FB_OBJECTS_BIAS_DM_2 = {
    1: {
        "A": "diamonds",
        "B": "transparent things",
        "C": "gems",
        "B_Obj": "transparent things",
    },
    2: {
        "A": "trees",
        "B": "tall things",
        "C": "plants",
        "B_Obj": "tall things",
    },
    3: {
        "A": "whales",
        "B": "big things",
        "C": "mammals",
        "B_Obj": "big thingss",
    },
    4: {
        "A": "famous actors",
        "B": "old people",
        "C": "wealthy people",
        "B_Obj": "old people",
    },
}

ALL_FB_OBJECTS_NONSENSE = {
    1: {
        "A": "guztan wobars",
        "B": "shnesive",
        "C": "flogers wobars",
        "B_Obj": "shnesive wobars",
    },
    2: {
        "A": "storf things",
        "B": "thip",
        "C": "terg blobs",
        "B_Obj": "things that thip",
    },
    3: {"A": "geck things", "B": "confive", "C": "blurst", "B_Obj": "confive things"},
}

ALL_FB_OBJECTS_TASK_FEW_SHOT = {
    1: {
        "A": "zoct",
        "B": "thrund",
        "C": "spuff",
        "B_Obj": "thrund",
    },
    2: {
        "A": "kleegs",
        "B": "biksy",
        "C": "feps",
        "B_Obj": "biksy",
    },
    3: {
        "A": "mutts",
        "B": "garky",
        "C": "fogers",
        "B_Obj": "garky",
    },
    4: {
        "A": "guztan wobars",
        "B": "shnesive",
        "C": "flogers wobars",
        "B_Obj": "shnesive wobars",
    },
    5: {
        "A": "storf things",
        "B": "thip",
        "C": "terg blobs",
        "B_Obj": "things that thip",
    },
}


FORMAT_FEW_SHOT_FB_1 = {
    "PREMISE1": "Price is $10 per soda",
    "PREMISE2": "Customer inserted $20",
    "CONCLUSION_VALID": "Customer can buy only two sodas",
    "CONCLUSION_INVALID": "Customer can buy only one soda",
}

FORMAT_FEW_SHOT_FB_2 = {
    "PREMISE1": "John had five apples",
    "PREMISE2": "John ate two apples",
    "CONCLUSION_VALID": "John has three apples left",
    "CONCLUSION_INVALID": "John has four apples left",
}

FORMAT_FEW_SHOT_FB_3 = {
    "PREMISE1": "The distance from the city to the lake is 10 miles",
    "PREMISE2": "The dog already walked 5 miles",
    "CONCLUSION_VALID": "The dog has 5 miles left",
    "CONCLUSION_INVALID": "The dog has 2 miles left",
}

FORMAT_FEW_SHOT_FB_4 = {
    "PREMISE1": "A pen costs $5",
    "PREMISE2": "A pencil costs $1",
    "CONCLUSION_VALID": "buying both the and the pencil would cost $6",
    "CONCLUSION_INVALID": "buying both the and the pencil would cost $5",
}


FORMAT_FEW_SHOT_FB_5 = {
    "PREMISE1": "Sara wants to buy a book that costs $12",
    "PREMISE2": "Sara has $5 saved",
    "CONCLUSION_VALID": "Sara could buy the book with an additional $8",
    "CONCLUSION_INVALID": "Sara could buy the book with and additional $4",
}

ALL_FB_FORMAT_FEW_SHOT = {
    1: FORMAT_FEW_SHOT_FB_1,
    2: FORMAT_FEW_SHOT_FB_2,
    3: FORMAT_FEW_SHOT_FB_3,
    4: FORMAT_FEW_SHOT_FB_4,
    5: FORMAT_FEW_SHOT_FB_5,
}

#################################################### Possible Answers ####################################################


def get_possible_answers(bias_name):
    if bias_name == "decoy":
        possible_answers = [
            (" Brand 1", -1),
            (" Brand 2", -1),
            (" Brand 3", -1),
        ]
    elif bias_name == "certainty":
        possible_answers = [
            (" Option A", -1),
            (" Option B", -1),
        ]
    elif bias_name == "false_belief":
        possible_answers = [
            (" The conclusion is valid", -1),
            (" The conclusion is invalid", -1),
            (" The argument is valid", -1),
            (" The argument is invalid", -1),
        ]
    else:
        raise Exception(
            f"Wrong bias name - got {bias_name}, only accepts decoy,certainty,false_belief"
        )
    return possible_answers
