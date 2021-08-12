import itertools
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from deva.score import score_model

model_dict = {
        'randomforest': RandomForestClassifier,
        'logistic': LogisticRegression
        }


def translate_config(cfg):
    '''toml cant make dictionaries with integer keys'''
    out = cfg.copy()
    if 'positive_class_weight' in out:
        w = out.pop('positive_class_weight')
        d = {0: 1, 1: w}
        out['class_weight'] = d
    return out


def iterate_hypers(base_cfg, range_cfg, list_cfg, instance_cfg, n_range_draws):
    if instance_cfg is not None:
        for set_name, params in instance_cfg.items():
            full_dict = base_cfg.copy()
            full_dict.update(params)
            yield set_name, full_dict

    if list_cfg is not None:
        iters = [[(pname, val) for val in l] for pname, l in list_cfg.items()]
        for i, kv in enumerate(itertools.product(*iters)):
            d = {k: v for (k, v) in kv}
            full_dict = base_cfg.copy()
            full_dict.update(d)
            yield f'list{i}', full_dict

    if range_cfg is not None:
        for i in range(n_range_draws):
            d = {k: np.random.uniform(v[0], v[1])
                 for k, v in range_cfg.items()}
            full_dict = base_cfg.copy()
            full_dict.update(d)
            yield f'range{i}', full_dict


def iter_models(X_train, y_train, t_train, X_test, y_test, t_test, cfg):

    model_str = set(model_dict.keys()).intersection(set(cfg.keys())).pop()

    metrics_cfg = cfg["metrics"]
    model_cfg = cfg[model_str]

    base_cfg = model_cfg.copy()
    range_cfg = None
    list_cfg = None
    instance_cfg = None
    if 'ranges' in base_cfg:
        range_cfg = base_cfg.pop('ranges')
    if 'lists' in base_cfg:
        list_cfg = base_cfg.pop('lists')
    if 'instances' in base_cfg:
        instance_cfg = base_cfg.pop('instances')

    piter = iterate_hypers(base_cfg, range_cfg, list_cfg,
                           instance_cfg, cfg['n_range_draws'])
    for param_name, param_dict in piter:
        processed_params = translate_config(param_dict)
        m = model_dict[model_str](**processed_params)
        m.fit(X_train, y_train)
        y_pred = m.predict(X_test)
        y_scores = m.predict_proba(X_test)[:, 1]
        model_scores = score_model(y_pred, y_scores, y_test, X_test,
                                   metrics_cfg)
        d = {
                'name': param_name,
                'model': m,
                'params': param_dict,
                'y_pred': y_pred,
                'y_scores': y_scores,
                'model_scores': model_scores
            }
        yield d
