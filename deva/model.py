from logging import info
# from sklearn.linear_model import LogisticRegression
# from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics


def build_model(X_train, y_train, t_train, X_test, y_test, t_test, cfg):

    # Build model and make prediction
    # clf = LogisticRegression(random_state=cfg.random_seed).fit(
    #     X_train, y_train)
    clf = RandomForestClassifier(random_state=cfg.random_seed).fit(
        X_train, y_train)
    pred_prob = clf.predict_proba(X_test)[:, 1]
    pred = clf.predict(X_test)

    # Write out validation data
    data_out = X_test.copy()
    data_out['is_fraud'] = y_test
    data_out['score'] = pred_prob
    data_out['is_flagged'] = pred

    data_out = data_out.join(t_test)
    data_out.sort_index(inplace=True)

    # check performance
    fpr, tpr, _thresholds = metrics.roc_curve(y_test, pred_prob, pos_label=1)
    auc = metrics.auc(fpr, tpr)
    info('AUC: {}'.format(auc))

    return data_out, clf
