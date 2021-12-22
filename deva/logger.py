from datetime import datetime


class Logger:
    ''' Class for logging options'''
    log = {}
    choice_number = 0

    def __init__(self, scenario, algo, name):
        self.log['profile'] = {}
        self.log['profile']['scenario'] = scenario
        self.log['profile']['algorithm'] = algo
        self.log['profile']['time'] = datetime.now()
        self.log['profile']['user'] = name
        self.log['choices'] = {}

    def add_choice(self, choice):
        self.log['choices']['Question number ' +
                            str(self.choice_number)] = choice
        self.choice_number += 1

    def add_result(self, result):
        self.log['result'] = result

    def get_log(self):
        return self.log
