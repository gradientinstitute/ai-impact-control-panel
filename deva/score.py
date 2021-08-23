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
# First element of the value tuple is a function to calculate the score.
# Second element of the value tuple is the optimal value of that score.
metrics_dict = {
        'accuracy': (model_acc, 1.),
        'auc': (model_auc, 1.),
        }


def score_model(y_pred, y_scores, y_test, X_test, metrics_cfg):
    # Evaluates the models outputs against predefinted metrics
    d = {}
    for k, v in metrics_cfg.items():
        score = metrics_dict[k][0](y_test, y_pred)
        d[v["name"]] = (score, metrics_dict[k][1])
    return d
