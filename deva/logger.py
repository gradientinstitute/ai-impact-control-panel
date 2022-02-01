"""Module to support eliciter logging."""
from copy import deepcopy
from datetime import datetime
from collections import OrderedDict


class Logger:
    ''' Class for logging options'''
    log = OrderedDict()
    choice_number = 0

    def __init__(self, scenario, algo, name):
        self.log['profile'] = {}
        self.log['profile']['scenario'] = scenario
        self.log['profile']['algorithm'] = algo
        self.log['profile']['time'] = datetime.now()
        self.log['profile']['user'] = name
        self.log['choices'] = {}
        self.log['result'] = None

    def add_options(self, option):
        option_store = deepcopy(option)
        for o in option_store:
            del o['name']
        self.log['choices']['Question number ' +
                            str(self.choice_number + 1)] =\
            {'options': option_store}

    def add_choice(self, choice):
        for key in choice[0].keys():
            self.log['choices']['Question number ' +
                                str(self.choice_number + 1)][key] =\
                                    choice[0][key]
        self.choice_number += 1

    def add_result(self, result):
        self.log["result"] = result

    def get_log(self):
        return self.log
