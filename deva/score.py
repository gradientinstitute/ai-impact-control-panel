import numpy as np
from sklearn import metrics


def model_auc(y_test, y_pred, _):
    fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred, pos_label=1)
    auc = metrics.auc(fpr, tpr)
    return auc


def model_acc(y_test, y_pred, _):
    fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred, pos_label=1)
    acc = np.mean(y_pred == y_test)
    return acc


def fn(y_test, y_pred, _):
    tn, fp, fn, tp = metrics.confusion_matrix(y_test, y_pred).ravel()
    return fn


def fp(y_test, y_pred, _):
    tn, fp, fn, tp = metrics.confusion_matrix(y_test, y_pred).ravel()
    return fp


def fnwo(y_test, y_pred, customer_id, cutoff):
    # compute how many customers have false negative errors > cutoff

    # Find false negatives
    fn_flag = y_test.astype(bool) & ~y_pred.astype(bool)
    # aggregate to customers
    cid, ix = np.unique(customer_id, return_inverse=True)
    counts = np.bincount(ix[fn_flag])
    return (counts>=cutoff).sum()


def fpwo(y_test, y_pred, customer_id, cutoff):
    # compute how many customers have false negative errors > cutoff

    # Find false negatives
    fp_flag = ~y_test.astype(bool) & y_pred.astype(bool)
    # aggregate to customers
    cid, ix = np.unique(customer_id, return_inverse=True)
    counts = np.bincount(ix[fp_flag])
    return (counts>=cutoff).sum()


def profit(y_test, y_pred, customer_id, TP, FP, TN, FN):
    # compute how many customers have false negative errors > cutoff
    confuse = metrics.confusion_matrix(y_test, y_pred).ravel()
    return np.dot(confuse, [TN, FP, FN, TP])


# A dictionary that maps config dictionary metric headings to functions.
# The key must match the heading in the model toml
# First element of the value tuple is a function to calculate the score.
# Second element of the value tuple is the optimal value of that score.
metrics_dict = {
        'accuracy': {'func': model_acc, 'optimal': 1., 'type': 'float'},
        'auc': {'func': model_auc, 'optimal': 1., 'type': 'float'},
        'fp': {'func': fp, 'optimal': 0, 'type': 'int'},
        'fn': {'func': fn, 'optimal': 0, 'type': 'int'},
        'fnwo': {'func': fnwo, 'optimal': 0, 'type': 'int'},
        'fpwo': {'func': fpwo, 'optimal': 0, 'type': 'int'},
        'profit': {'func': profit, 'optimal': 1e8, 'type': 'float'},
        }


def score_model(y_pred, y_scores, y_test, X_test, metrics_cfg, customer_id):

    # Evaluates the models outputs against predefinted metrics
    d = {}
    CID = X_test.customer_id  # TODO - how do we ensure

    for k, v in metrics_cfg.items():
        args = {key:v[key] for key in v if key != "name"}
        score = metrics_dict[k]['func'](y_test, y_pred, customer_id, **args)
        d[v["name"]] = {'score': score, 'optimal': metrics_dict[k]['optimal'],
                        'type': metrics_dict[k]['type']}

    return d
