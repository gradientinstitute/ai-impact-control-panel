'''Reference "models" for conceptual aid.'''

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils import check_array, check_X_y, check_random_state
from sklearn.utils.validation import check_is_fitted
from sklearn.preprocessing import LabelBinarizer


class RandomClassifier(BaseEstimator, ClassifierMixin):
    '''Random classifier for predicting randomly using the label base rate.

    If a sensitive attribute is provided, then this class will also stratify
    the base rates based on this attribute.

    Parameters
    ----------
    stratify_attribute: int, str, optional
        This is an integer or string specifying the column index into X of the
        attribute to use to compute the base rates. If this is None, then the
        base rate of labels is used for all of the data. Otherwise this column
        will indicate how to split the labels into different groups, and a base
        rate for each group will be computed.
    random_state: None, int or RandomState
        An int seed for to control the random state, or a numpy RandomState
        object.

    Note
    ----
    This only works on binary labels so far.
    '''

    def __init__(
        self,
        stratify_attribute=None,
        random_state=None
    ):
        '''Construct a random classifier object.'''
        if not isinstance(stratify_attribute, (str, int)) and \
                stratify_attribute is not None:
            raise TypeError('stratify_attribute must be a string or integer')
        self.stratify_attribute = stratify_attribute
        self.random_state = check_random_state(random_state)

    def fit(self, X, y):
        '''Fit a random classifier.

        Parameters
        ----------
        X: ndarray or DataFrame
            A shape (N, D) array of covariates. If stratify_attribute has been
            specified, then this specifies the column into X of the attribute
            to use for label stratification.
        y: ndarray
            The labels used to compute the base rates.
        '''
        self.labelenc_ = LabelBinarizer()
        if isinstance(self.stratify_attribute, str):
            if not hasattr(X, 'columns'):
                raise TypeError('X has to be a DataFrame,'
                                'or use int stratify_attribute')
            self.sens_col_ = list(X.columns).index(self.stratify_attribute)
        else:
            self.sens_col_ = self.stratify_attribute
        X, y = check_X_y(X, y)

        ye = self.labelenc_.fit_transform(y)
        if len(self.labelenc_.classes_) != 2:
            raise ValueError('RandomClassifier only works with binary labels.')

        if self.stratify_attribute is None:
            self.py_ = ye.mean()
        else:
            A = X[:, self.sens_col_]
            self.a_classes_ = set(A)
            self.py_ = [y[A == a].mean() for a in self.a_classes_]

        return self

    def predict(self, X):
        '''Use a random classifier for prediction.

        Parameters
        ----------
        X: ndarray or DataFrame
            A shape (N, D) array of covariates. If stratify_attribute has been
            specified, then this specifies the column into X of the attribute
            to use for label stratification. This will change the probability
            of predicting y==1 for each attribute class.

        Returns
        -------
        y: ndarray
            An array of shape (N,) of predictions. These predictions are
            random, with a probability defined by the training label base rates
            (for each sensitive attribute if stratify_attribute has been set).
        '''
        py = self.predict_proba(X)[:, 1]
        y_hat = self.random_state.binomial(n=1, p=py)
        return self.labelenc_.inverse_transform(y_hat)

    def predict_proba(self, X):
        '''Use a random classifier for probabilistic prediction.

        Parameters
        ----------
        X: ndarray or DataFrame
            A shape (N, D) array of covariates. If stratify_attribute has been
            specified, then this specifies the column into X of the attribute
            to use for label stratification. This will change the probability
            of predicting y==1 for each attribute class.

        Returns
        -------
        py: ndarray
            An array of shape (N, 2) of class probability predictions. These
            probabilities are the (unconditional) base rate probabilities, p(y)
            defined by the training label base rates. If stratify_attribute is
            not None, then these are conditional, p(y|a), where a is the
            attribute.
        '''
        check_is_fitted(self, attributes=['py_'])
        X = check_array(X)
        n = len(X)

        py = np.zeros((n, len(self.labelenc_.classes_)))
        if self.stratify_attribute is None:
            py[:, 1] = self.py_
            py[:, 0] = 1 - self.py_
            return py

        A = X[:, self.sens_col_]
        for i, a in enumerate(self.a_classes_):
            py[A == a, 1] = self.py_[i]
        py[:, 0] = 1. - py[:, 1]

        return py

    def get_params(self, deep=True):
        """Get this estimator's initialisation parameters."""
        return {
            'stratify_attribute': self.stratify_attribute
        }

    def set_params(self, **parameters):
        """Set this estimator's initialisation parameters."""
        for parameter, value in parameters.items():
            setattr(self, parameter, value)
        return self

    def _get_tags(self):
        tags = super()._get_tags()
        tags['binary_only'] = True  # tell sklearn API this is binary only
        return tags
