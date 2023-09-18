CHOICE_OPTIONS = {
    "1": 1,
    "first": 1,
    "A": 1,
    "2": 2,
    "second": 2,
    "B": 2,
    "3": 3,
    "third": 3,
    "C": 3,
}


TRUE_OPTIONS = {
    option: True
    for option in ["Yes", "yes", "True", "true", "Valid", "valid", "Correct", "correct"]
}

FALSE_OPTIONS = {
    option: False
    for option in [
        "No",
        "no",
        "False",
        "false",
        "Invalid",
        "invalid",
        "Incorrect",
        "incorrect",
    ]
}

ANSWERS_TOKENS = {
    "decoy": CHOICE_OPTIONS,
    "certainty": CHOICE_OPTIONS,
    "false_belief": TRUE_OPTIONS | FALSE_OPTIONS,
}
