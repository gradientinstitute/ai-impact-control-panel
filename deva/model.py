import itertools
import numpy as np

from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.dummy import DummyClassifier

from deva.score import score_model
from deva.references import RandomClassifier

model_dict = {
    'randomforest': RandomForestClassifier,
    'logistic': LogisticRegression,
    'adaboost': AdaBoostClassifier,
    'svm': SVC,
    'randomclassifier': RandomClassifier,
    'dummyclassifier': DummyClassifier
}


def translate_config(cfg):
    '''toml cant make dictionaries with integer keys'''
    out = cfg.copy()
    if 'positive_class_weight' in out:
        w = out.pop('positive_class_weight')
        d = {0: 1, 1: w}
        out['class_weight'] = d
    return out


def apply_threshold(
    threshold,
    threshold_protected,
    y_scores,
    sensitive_indicator
):
    '''apply binary threshold(s) to a score.'''
    if threshold_protected is None:
        y_pred = (y_scores > threshold).astype(int)
        return y_pred

    if sensitive_indicator is None:
        raise TypeError('a protected attribute must be defined to apply '
                        'separate thresholds.')

    sind = sensitive_indicator.astype(bool)
    y_pred = np.zeros(len(y_scores), dtype=int)
    y_pred[sind] = y_scores[sind] > threshold_protected
    y_pred[~sind] = y_scores[~sind] > threshold

    return y_pred


def iter_hypers(base_cfg, range_cfg, list_cfg, instance_cfg, n_range_draws):
    for model_name, instance_items in instance_cfg.items():
        for set_name, params in instance_items.items():
            full_dict = base_cfg[model_name].copy()
            full_dict.update(params)
            yield model_name, set_name, full_dict

    for model_name, list_items in list_cfg.items():
        iters = [[(pname, v) for v in l] for pname, l in list_items.items()]
        for i, kv in enumerate(itertools.product(*iters)):
            d = {k: v for (k, v) in kv}
            full_dict = base_cfg[model_name].copy()
            full_dict.update(d)
            yield model_name, f'list{i}', full_dict

    for model_name, range_items in range_cfg.items():
        for i in range(n_range_draws):
            d = {k: np.random.uniform(v[0], v[1])
                 for k, v in range_items.items()}
            full_dict = base_cfg[model_name].copy()
            full_dict.update(d)
            yield model_name, f'range{i}', full_dict


def iter_models(X_train, y_train, t_train, X_test, y_test, t_test, cfg):

    model_keys = set(model_dict.keys()).intersection(set(cfg.keys()))
    metrics_cfg = cfg["metrics"]
    base_cfg = {}
    range_cfg = {}
    list_cfg = {}
    instance_cfg = {}

    for model_key in model_keys:
        model_cfg = cfg[model_key]
        base_cfg[model_key] = model_cfg.copy()
        if 'ranges' in base_cfg[model_key]:
            range_cfg[model_key] = base_cfg[model_key].pop('ranges')
        if 'lists' in base_cfg[model_key]:
            list_cfg[model_key] = base_cfg[model_key].pop('lists')
        if 'instances' in base_cfg[model_key]:
            instance_cfg[model_key] = base_cfg[model_key].pop('instances')

    # Pull out the sensitive attribute indicator if it exists
    sensitive_indicator = None
    if 'sensitive_attribute' in cfg:
        sensitive_indicator = X_test.loc[:, cfg['sensitive_attribute']]

    # Attempt to extract customer id
    customer_id = None
    if 'customer_id' in cfg:
        customer_id = X_test[cfg['customer_id']].values.astype(int)

    piter = iter_hypers(base_cfg, range_cfg, list_cfg, instance_cfg,
                        cfg['n_range_draws'])
    for model_str, param_name, param_dict in piter:
        processed_params = translate_config(param_dict)
        threshold = processed_params.pop('threshold', None)
        threshold_protected = processed_params.pop('threshold_protected', None)
        m = model_dict[model_str](**processed_params)
        m.fit(X_train, y_train)
        y_scores = m.predict_proba(X_test)[:, 1]  # NOTE: assumes binary class.
        if threshold is None:
            y_pred = m.predict(X_test)
        else:
            y_pred = apply_threshold(threshold, threshold_protected, y_scores,
                                     sensitive_indicator)
        model_scores = score_model(y_pred, y_scores, y_test, X_test,
                                   metrics_cfg, customer_id,
                                   sensitive_indicator)
        d = {
                'name': f'{model_str}_{param_name}',
                'model': m,
                'params': param_dict,
                'y_pred': y_pred,
                'y_scores': y_scores,
                'model_scores': model_scores
            }
        yield d
