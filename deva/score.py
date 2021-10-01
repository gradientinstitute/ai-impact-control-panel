import numpy as np
from sklearn import metrics

_TN = (0, 0)
_TP = (1, 1)
_FN = (1, 0)
_FP = (0, 1)


def model_auc(y_test, y_pred, *_):
    fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred, pos_label=1)
    auc = metrics.auc(fpr, tpr)
    return auc


def model_acc(y_test, y_pred, *_):
    acc = np.mean(y_pred == y_test)
    return acc


def fn(y_test, y_pred, *_):
    tn, fp, fn, tp = metrics.confusion_matrix(y_test, y_pred).ravel()
    return fn


def fp(y_test, y_pred, *_):
    tn, fp, fn, tp = metrics.confusion_matrix(y_test, y_pred).ravel()
    return fp


def fn_cvar(y_test, y_pred, customer_id, _, alpha):
    """Compute average fn of the worst off individuals."""
    fn_flag = y_test.astype(bool) & ~y_pred.astype(bool)
    return _cvar(fn_flag, customer_id, alpha)


def fp_cvar(y_test, y_pred, customer_id, _, alpha):
    """Compute average fn of the worst off individuals."""
    fp_flag = ~y_test.astype(bool) & y_pred.astype(bool)
    return _cvar(fp_flag, customer_id, alpha)


def _cvar(flag, cid, alpha):
    # aggregate to customers
    assert 0 < alpha < 1
    uid, ix = np.unique(cid, return_inverse=True)
    counts = np.sort(np.bincount(ix[flag], minlength=len(uid)))
    assert len(counts)
    # tail will always include at least a single worst off person
    tail = max(1, int(len(counts) * alpha + 0.5))
    tailc = counts[-tail:]
    return tailc.mean()


def fnwo(y_test, y_pred, customer_id, _, cutoff):
    # compute how many customers have false negative errors > cutoff

    # Find false negatives
    fn_flag = y_test.astype(bool) & ~y_pred.astype(bool)
    # aggregate to customers
    cid, ix = np.unique(customer_id, return_inverse=True)
    counts = np.bincount(ix[fn_flag])
    return (counts >= cutoff).sum()


def fpwo(y_test, y_pred, customer_id, _, cutoff):
    # compute how many customers have false negative errors > cutoff

    # Find false negatives
    fp_flag = ~y_test.astype(bool) & y_pred.astype(bool)
    # aggregate to customers
    cid, ix = np.unique(customer_id, return_inverse=True)
    counts = np.bincount(ix[fp_flag])
    return (counts >= cutoff).sum()


def profit(y_test, y_pred, customer_id, _, TP, FP, TN, FN):
    # compute how many customers have false negative errors > cutoff
    confuse = metrics.confusion_matrix(y_test, y_pred).ravel()
    return np.dot(confuse, [TN, FP, FN, TP])


def eo_disadv_rate(y_test, y_pred, _, sens_attrib):
    '''Equality of opportunity rate difference for the disadvantaged class.

        EO = max(0, TPR_adv - TPR_dis)
    '''
    return _eo(y_test, y_pred, sens_attrib, True, True)


def eo_adv_rate(y_test, y_pred, _, sens_attrib):
    '''Equality of opportunity rate difference for the advantaged class.

        EO = max(0, TPR_dis - TPR_adv)
    '''
    return _eo(y_test, y_pred, sens_attrib, False, True)


def eo_disadv(y_test, y_pred, _, sens_attrib):
    '''Equality of opportunity difference for the disadvantaged class.
        EO = max(0, TP_adv - TP_dis)
    '''
    return _eo(y_test, y_pred, sens_attrib, True, False)


def eo_adv(y_test, y_pred, _, sens_attrib):
    '''Equality of opportunity difference for the advantaged class.
        EO = max(0, TP_dis - TP_adv)
    '''
    return _eo(y_test, y_pred, sens_attrib, False, False)


def _eo(y_test, y_pred, sens_attrib, disadvantage, rate):
    # Equal opportunity
    confuse_sens = metrics.confusion_matrix(
        y_test[sens_attrib == 1],
        y_pred[sens_attrib == 1]
    )
    confuse_nonsens = metrics.confusion_matrix(
        y_test[sens_attrib == 0],
        y_pred[sens_attrib == 0]
    )
    tp_sens = _tpr(confuse_sens) if rate else confuse_sens[_TP]
    tp_nonsens = _tpr(confuse_nonsens) if rate else confuse_nonsens[_TP]

    diff = tp_nonsens - tp_sens
    eq_opp = max(0, diff if disadvantage else -diff)
    return eq_opp


def _tpr(confmat):
    tpr = confmat[_TP] / (confmat[_TP] + confmat[_FN])
    return tpr


# A dictionary that maps config dictionary metric headings to functions.
# The key must match the heading in the model toml
# First element of the value tuple is a function to calculate the score.
# Second element of the value tuple is the optimal value of that score.
# TODO: optimal doesn't belong here anymore
metrics_dict = {
        'accuracy': {'func': model_acc, 'optimal': 'max', 'type': 'float'},
        'auc': {'func': model_auc, 'optimal': 'max', 'type': 'float'},
        'fp': {'func': fp, 'optimal': 'min', 'type': 'int'},
        'fn': {'func': fn, 'optimal': 'min', 'type': 'int'},
        'fn_cvar': {'func': fn_cvar, 'optimal': 'min', 'type': 'int'},
        'fp_cvar': {'func': fp_cvar, 'optimal': 'min', 'type': 'int'},
        'fnwo': {'func': fnwo, 'optimal': 'min', 'type': 'int'},
        'fpwo': {'func': fpwo, 'optimal': 'min', 'type': 'int'},
        'profit': {'func': profit, 'optimal': 'max', 'type': 'float'},
        'eo_advantage':
                {'func': eo_adv, 'optimal': 'min', 'type': 'float'},
        'eo_disadvantage':
                {'func': eo_disadv, 'optimal': 'min', 'type': 'float'},
        'eo_advantage_rate':
                {'func': eo_adv_rate, 'optimal': 'min', 'type': 'float'},
        'eo_disadvantage_rate':
                {'func': eo_disadv_rate, 'optimal': 'min', 'type': 'float'},
        }


def score_model(y_pred, y_scores, y_test, X_test,
                metrics_cfg, customer_id,
                sensitive_indicator):

    # Evaluates the models outputs against predefinted metrics
    d = {}

    for k, v in metrics_cfg.items():
        args = {key: v[key] for key in v if key != "name"}
        score = metrics_dict[k]['func'](y_test, y_pred,
                                        customer_id, sensitive_indicator,
                                        **args)
        d[v["name"]] = {'score': score, 'optimal': metrics_dict[k]['optimal'],
                        'type': metrics_dict[k]['type']}

    return d
