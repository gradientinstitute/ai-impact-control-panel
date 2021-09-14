import numpy as np
from deva.halfspace import HalfspaceMax, HalfspaceRanking


class Pairwise:
    '''Pairwise comparison.'''
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __contains__(self, x):
        return (x==self.a) | (x == self.b)

    def __getitem__(self, index):
        if index == 0:
            return self.a
        elif index == 1:
            return self.b
        else:
            raise IndexError()

    def invert(self, x):
        if (x==self.a):
            return self.b
        elif (x==self.b):
            return self.a
        else:
            raise ValueError(f"{x} not in [{self.a}, {self.b}]")


    def json(self):
        '''return a representation to send to the front-end'''
        return {
            "type": "pairwise",
            "options": [self.a, self.b],
        }


class Eliciter:
    '''Base class for elicitation algorithms.'''
    terminated = True  # finished
    query = None  # current question
    result = None  # terminating choice

    def __init__(self, models):
        raise NotImplementedError

    def update(self, choice):
        raise NotImplementedError


class Toy(Eliciter):

    def __init__(self, models):
        '''Simple eliciter with sequential elimination.'''
        self._candidates = list(models.keys())
        self._update_query()

    def update(self, choice):
        '''Process user-preference.'''
        if choice in self.query:
            self._candidates.remove(self.query.invert(choice))
            self._update_query()

    def _update_query(self):
        if len(self.candidates) == 1:
            self.terminated = True
            self.result = self.candidates[0]
        else:
            self.terminated = False
            self.query = Pairwise(self.candidates[0], self.candidates[1])



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
