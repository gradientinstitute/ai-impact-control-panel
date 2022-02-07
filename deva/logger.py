"""Module to support eliciter logging."""
from copy import deepcopy
from datetime import datetime
from collections import OrderedDict


class Logger:
    """Class for logging options."""

    log = OrderedDict()
    choice_number = 0

    def __init__(self, scenario, algo, name):
        self.log["profile"] = {}
        self.log["profile"]["scenario"] = scenario
        self.log["profile"]["algorithm"] = algo
        self.log["profile"]["time"] = datetime.now()
        self.log["profile"]["user"] = name
        self.log["choices"] = {}
        self.log["result"] = None

    def add_options(self, option):
        """Log a query presented to the user."""
        option_store = deepcopy(option)
        for o in option_store:
            del o["name"]
        self.log["choices"]["Question number "
                            + str(self.choice_number + 1)] =\
            {"options": option_store}

    def add_choice(self, choice):
        """Log a decision made by the user."""
        for key in choice[0].keys():
            question = "Question number " + str(self.choice_number + 1)
            self.log["choices"][question][key] = choice[0][key]
        self.choice_number += 1

    def add_result(self, result):
        """Log the result of an eliciter algorithm."""
        self.log["result"] = result
