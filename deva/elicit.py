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



