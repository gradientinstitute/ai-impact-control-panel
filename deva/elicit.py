import numpy as np
from deva.halfspace import rank_ex


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


class ActiveRanking(Eliciter):

    def __init__(self, models):
        model_feats = []
        self.model_attrs = []
        self.model_names = []
        for k, v in models.items():
            self.model_names.append(k)
            self.model_attrs.append(v)
            model_feats.append([s['score'] for s in v.values()])
        model_feats = np.array(model_feats)
        self.ranks = np.zeros(len(self.model_names), dtype=int)
        self.ranker = rank_ex(model_feats, self.ranks, True)
        self.response = None
        self.query = None
        self.query_map = {}

    def finished(self):
        try:
            if self.response is None:
                self.query = next(self.ranker)
            else:
                self.query = self.ranker.send(self.response)
            return False
        except StopIteration:
            return True

    def prompt(self):
        if self.query is not None:
            a, b = self.query
            self.query_map = {self.model_names[a]: 1, self.model_names[b]: -1}
            qa = (self.model_names[a], self.model_attrs[a])
            qb = (self.model_names[b], self.model_attrs[b])
            return qa, qb
        else:
            raise RuntimeError('User prompted before algorithm initialised.')

    def user_input(self, txt):
        if txt in self.query_map:
            self.response = self.query_map[txt]
            return txt
        else:
            None

    def final_output(self):
        best_ind = self.ranks[-1]
        return self.model_names[best_ind], self.model_attrs[best_ind]
