import numpy as np
from deva.halfspace import HalfspaceMax, HalfspaceRanking


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

    _active_alg = HalfspaceRanking

    def __init__(self, models):
        model_feats = []
        self.model_attrs = []
        self.model_names = []
        for k, v in models.items():
            self.model_names.append(k)
            self.model_attrs.append(v)
            model_feats.append([s['score'] for s in v.values()])
        model_feats = np.array(model_feats)
        self.active = self._active_alg(model_feats, True)
        self.query_map = {}

    def finished(self):
        return not self.active.next_round()

    def prompt(self):
        a, b = self.active.get_query()
        self.query_map = {self.model_names[a]: 1, self.model_names[b]: -1}
        qa = (self.model_names[a], self.model_attrs[a])
        qb = (self.model_names[b], self.model_attrs[b])
        return qa, qb

    def user_input(self, txt):
        if txt in self.query_map:
            self.active.put_response(self.query_map[txt])
            return txt
        else:
            return None

    def final_output(self):
        res = self.active.get_result()
        if res is None:
            raise RuntimeError('Final result not ready.')
        best_ind = res[-1]
        return self.model_names[best_ind], self.model_attrs[best_ind]


class ActiveMax(ActiveRanking):

    _active_alg = HalfspaceMax

    def final_output(self):
        res = self.active.get_result()
        if res is None:
            raise RuntimeError('Final result not ready.')
        return self.model_names[res], self.model_attrs[res]
