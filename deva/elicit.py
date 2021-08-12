

class Eliciter:

    def finished(self):
        raise NotImplementedError

    def prompt(self):
        raise NotImplementedError

    def user_input(self, input):
        raise NotImplementedError

    def final_output(self):
        raise NotImplementedError


class Toy(Eliciter):

    def __init__(self, models):
        '''Create new eliciter. Models is a dict with keys as model names
        and values as dicts of performance metrics'''

        self.models = models
        self.result = None
        self.result_name = None
        self.candidates = list(self.models.keys())

    def finished(self):
        if len(self.candidates) == 1:
            self.result_name = self.candidates[0]
            self.result = self.models[self.result_name]
            return True
        else:
            return False

    def prompt(self):
        # get two models
        m1 = self.candidates[0]
        m2 = self.candidates[1]
        self.just_asked = [m1, m2]
        return (m1, self.models[m1]), (m2, self.models[m2])

    def user_input(self, txt):
        if txt in self.just_asked:
            self.just_asked.remove(txt)
            # delete the one they didnt like
            self.candidates.remove(self.just_asked[0])
            return txt
        else:
            return None

    def final_output(self):
        return self.result_name, self.result
