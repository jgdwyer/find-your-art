import numpy as np
import pandas as pd
import webapp.model
import random

def validate_on_year():
    df = pd.read_pickle('./webapp/webapp/static/art_yr_label_cln2_cats_labs_sparse.pickle')
    # Limit to entries with year values
    df = df[df['date']>0].reset_index(drop=True)
    yrs = np.arange(1607, 1910)
    # Loop over dataframe and calculate error from year
    err = np.zeros(len(yrs))
    err_base = np.zeros(len(yrs))
    for i, yr in enumerate(yrs):
        err[i] = _validate_on_year(df, yr, algorandom=False)
        err_base[i] = _validate_on_year(df, yr, algorandom=True)
        print('----------')
        print(yr)
        print('Err: {:.3f} vs Randerr: {:.3f}'.format(err[i], err_base[i]))
        print('----------')
    return err, err_base

def _validate_on_year(df, year, algorandom=False):
    """Selects a few images randomly with the same year as the input variable
    and measures accuracy of prediction"""
    # Pick three entries with the same year as that selected (or output nan)
    df_yr = df[df['date']==year].reset_index(drop=True)
    if len(df_yr)<7:
        return np.nan
    # Choose random entries from the df_yr dataframe
    inner_inds = random.sample(range(len(df_yr)), 3)
    # Get the index value in the big dataframe of these df_yr dataframe entries
    good_inds = df_yr.iloc[inner_inds].index.tolist()
    # Pick three entries with a random year (bad inds)
    bad_inds = random.sample(range(len(df)),3)
    # Set a few extra parameters
    db = None
    con = None
    do_db = None
    if algorandom:
        best_inds = random.sample(range(len(df)),4)
    else:
        best_inds = webapp.model.imgs_from_cats(good_inds, bad_inds, df, db, con, do_db)
    # Calculate how far dates of best inds are from the input year
    pred_years = np.zeros(len(best_inds))
    mse = 0.
    for i, b in enumerate(best_inds):
        pred_years[i] = df['date'].iloc[[b]].values[0]
        print(pred_years[i])
        mse += np.abs(pred_years[i] - year)
    print('-----')
    mse = mse / len(best_inds)
    return mse
