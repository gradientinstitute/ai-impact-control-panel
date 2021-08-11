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


# A dictionary that maps config dictionary metric headings to functions
metrics_dict = {
        'accuracy': model_acc,
        'auc': model_auc
        }


def score_model(y_pred, y_scores, y_test, X_test, metrics_cfg):
    # Evaluates the models outputs against predefinted metrics
    d = {}
    for k, v in metrics_cfg.items():
        score = metrics_dict[k](y_test, y_pred)
        d[v["name"]] = score
    return d
