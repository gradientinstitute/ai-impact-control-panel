"""
Generate and save fraud features and responses to csv.
"""
import numpy as np
import pandas as pd
from logging import info


def simulate(cfg):

    np.random.seed(cfg.random_seed)

    # generate some customers
    cust_id = np.arange(cfg.n_customers)

    # assign the customers gender
    cust_isfemale = np.random.rand(cfg.n_customers) < cfg.frac_female
    cust_ismale = np.logical_not(cust_isfemale)

    # assign high transactor
    cust_ishightrans = np.random.rand(cfg.n_customers) < cfg.frac_high_trans

    # a latent wealth variable
    # couple with gender?
    # cust_wealth = np.random.pareto(cfg.wealth_spread, size=cfg.n_customers)

    # a latent spending frequency
    # couple with wealth and or gender?
    cust_spendfreq = np.random.beta(cfg.cust_spend_alpha,
                                    cfg.cust_spend_beta,
                                    size=cfg.n_customers)
    # a latent fraud risk
    # couple with all the things
    cust_fraudrisk = np.random.beta(cfg.cust_risk_alpha,
                                    cfg.cust_risk_beta,
                                    size=cfg.n_customers)
    cust_fraudrisk = cust_fraudrisk / np.sum(cust_fraudrisk) * \
        cfg.frac_fraud * cfg.n_customers

    # Multiply by extra fraud risk to high spenders
    cust_fraudrisk[cust_ishightrans] *= cfg.high_spend_fraud

    # generate transactions
    trans_customer = np.random.choice(cust_id, size=cfg.n_transactions,
                                      replace=True,
                                      p=cust_spendfreq/np.sum(cust_spendfreq))
    trans_id = np.arange(cfg.n_transactions) + 1
    trans_ismale = cust_ismale[trans_customer]
    trans_isfemale = cust_isfemale[trans_customer]

    # Generate a transaction amount based on whether they are a high spender
    trans_highvalue_cust = cust_ishightrans[trans_customer]
    trans_amount = np.zeros(len(trans_highvalue_cust))
    low_amount = np.random.beta(cfg.low_alpha, cfg.low_beta,
                                size=np.sum(~trans_highvalue_cust))
    high_amount = np.random.beta(cfg.high_alpha, cfg.high_beta,
                                 size=np.sum(trans_highvalue_cust))
    trans_amount[~trans_highvalue_cust] = low_amount
    trans_amount[trans_highvalue_cust] = high_amount

    # generate label
    trans_fraud = (np.random.rand(
        cfg.n_transactions) < cust_fraudrisk[trans_customer]).astype(int)

    # generate transaction times in seconds
    trans_time = (np.random.beta(cfg.trans_time_alpha, cfg.trans_time_beta,
                                 size=cfg.n_transactions))
    trans_day = np.random.choice(np.arange(cfg.n_days),
                                 size=cfg.n_transactions,
                                 replace=True)
    abs_trans_time = np.sort(((trans_time + trans_day) *
                              3600 * 24).astype(int))

    # Generate transaction features
    # couple with customer features
    n_features = cfg.features
    X_latent = np.vstack((trans_fraud, trans_ismale, trans_highvalue_cust)).T
    W_start = np.random.randn(X_latent.shape[1], n_features)
    W_end = np.random.randn(X_latent.shape[1], n_features)

    # how much of W_end for each transaction
    W_trans_factor = np.linspace(0.0, cfg.nonstationarity, cfg.n_transactions)
    W = W_start[None, ...] + W_end[None, ...] * W_trans_factor[:, None, None]
    X_clean = np.matmul(X_latent[:, None, :], W).squeeze()
    X = cfg.signal_strength * X_clean + \
        cfg.noise * np.random.randn(cfg.n_transactions, n_features)

    if cfg.nonlinear:
        X = np.arctan(X)

    # Generate dataframe and save to disk
    feature_names = ['feature_{}'.format(i) for i in range(n_features)]
    columns = feature_names + ['customer_id',
                               'trans_time',
                               'trans_dollars',
                               'customer_is_male',
                               'customer_is_female',
                               'is_fraud']
    cols = np.concatenate((X, np.vstack((trans_customer,
                                         abs_trans_time,
                                         trans_amount,
                                         trans_ismale, trans_isfemale,
                                         trans_fraud)).T),
                          axis=1)
    df = pd.DataFrame(cols, columns=columns)
    df["trans_id"] = trans_id
    df.set_index("trans_id", inplace=True)
    df.isPrimary = 1

    info(f'Generated {df.shape[0]} instances of {df.shape[1]} features')

    # Split data into train and validation based on frac_data_validation in the
    # config file.
    train = df[:int(len(df) * (1 - cfg.frac_days_validation))]
    val = df[int(len(df) * (1 - cfg.frac_days_validation)):]

    return train, val
