import numpy as np
from sklearn import metrics


def model_auc(y_test, y_pred):
    fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred, pos_label=1)
    auc = metrics.auc(fpr, tpr)
    return auc


def model_acc(y_test, y_pred):
    fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred, pos_label=1)
    acc = np.mean(y_pred == y_test)
    return acc


def fn(y_test, y_pred):
    tn, fp, fn, tp = metrics.confusion_matrix(y_test, y_pred).ravel()
    return fn


def fp(y_test, y_pred):
    tn, fp, fn, tp = metrics.confusion_matrix(y_test, y_pred).ravel()
    return fp


# A dictionary that maps config dictionary metric headings to functions.
# The key must match the heading in the model toml
# First element of the value tuple is a function to calculate the score.
# Second element of the value tuple is the optimal value of that score.
metrics_dict = {
        'accuracy': {'func': model_acc, 'optimal': 1., 'type': 'float'},
        'auc': {'func': model_auc, 'optimal': 1., 'type': 'float'},
        'fp': {'func': fp, 'optimal': 0, 'type': 'int'},
        'fn': {'func': fn, 'optimal': 0, 'type': 'int'},
        }


def score_model(y_pred, y_scores, y_test, X_test, metrics_cfg):
    # Evaluates the models outputs against predefinted metrics
    d = {}
    for k, v in metrics_cfg.items():
        score = metrics_dict[k]['func'](y_test, y_pred)
        d[v["name"]] = {'score': score, 'optimal': metrics_dict[k]['optimal'],
                        'type': metrics_dict[k]['type']}

    return d