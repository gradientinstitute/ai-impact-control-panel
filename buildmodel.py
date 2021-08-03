# Copyright Gradient Institute Ltd 2020-2021. This software includes intellectual property owned by 
# Gradient Institute Ltd. Gradient Institute Ltd grants to UNIONBANK OF THE PHILIPPINES and its 
# Affiliates a perpetual, non-exclusive, non-transferable, worldwide use license over the intellectual property.

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
import matplotlib.pyplot as plt
import pandas as pd
import click
import ubpdash.config.model as cfg
from shapash.explainer.smart_explainer import SmartExplainer

@click.command()
@click.option('--shapash',
              type=click.Choice(['on', 'off']),
              default='off')
def cli(shapash):
    # Load train data
    df = pd.read_csv("data/synthetic_train_data.csv")
    df.set_index("ID", inplace=True)
    X_train = df.drop(["trans_time", "response"], axis=1)
    y_train = df.response
    t_train = df.trans_time

    # Load validation data
    df_val = pd.read_csv("data/synthetic_val_data.csv")
    df_val.set_index("ID", inplace=True)
    X_test = df_val.drop(["trans_time", "response"], axis=1)
    y_test = df_val.response
    t_test = df_val.trans_time


    # Build model and make prediction
    # clf = LogisticRegression(random_state=cfg.random_seed).fit(
    #     X_train, y_train)
    clf = RandomForestClassifier(random_state=cfg.random_seed).fit(
        X_train, y_train)
    pred_prob = clf.predict_proba(X_test)[:, 1]
    pred = clf.predict(X_test)

    # Write out validation data
    data_out = X_test.copy()
    data_out['response'] = y_test
    data_out['Adjprob'] = pred_prob
    data_out['Adjpred'] = pred

    #Adj probabilities to match ubp
    data_out['Adjprob'] *= cfg.AdjScale

    data_out = data_out.join(t_test)
    data_out.sort_index(inplace=True)
    data_out.to_csv("data/validation_data.csv")
    print("Validation data written successfully.")

    # Show performance
    fpr, tpr, thresholds = metrics.roc_curve(y_test, pred_prob, pos_label=1)
    auc = metrics.auc(fpr, tpr)
    print("AUC: {}".format(auc))
    plt.plot(fpr, tpr)
    plt.title("Fraud detector ROC. AUC: {:.2f}".format(auc))
    plt.show()

    #Write the model to disk
    from joblib import dump
    dump(clf, "data/model.joblib")

    if shapash == "on":
        shapash_frac = 0.01

        shapash_id = np.random.choice(np.array(len(X_test)), int(len(X_test) *
                                                                 shapash_frac),
                                      replace=False)
        xpl = SmartExplainer()
        xpl.compile(x=X_test.iloc[shapash_id], model=clf,
                    y_pred=pd.DataFrame(pred[shapash_id], columns=["pred"],
                                        index=X_test.iloc[shapash_id].index))
        app = xpl.run_app(title_story="Tips Dataset")
