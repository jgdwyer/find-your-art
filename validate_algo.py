import numpy as np
import pandas as pd
import webapp.model
import random

def validate_on_artist(verbose=False):
    df = pd.read_pickle('./webapp/webapp/static/art_yr_label_cln2_cats_labs_sparse.pickle')
    # Limit to entries with year values
    df = df[df['date']>0].reset_index(drop=True)
    artists = df['artist_name'].unique()
    # Loop over dataframe and calculate error from year
    err = np.empty(len(artists))
    err_base = np.empty(len(artists))
    err[:], err_base[:] = np.nan, np.nan
    print(len(artists))
    for i, artist in enumerate(artists):
        if sum(df['artist_name']==artist) >= 7:
            print(i)
            err[i] = _validate_on_artist2(df, artist, algorandom=False, verbose=verbose)
            err_base[i] = _validate_on_artist2(df, artist, algorandom=True, verbose=verbose)
            print('----------')
            print(artist)
            print('Err: {:.3f} vs Randerr: {:.3f}'.format(err[i], err_base[i]))
            print('----------')
    return err, err_base

def _validate_on_artist2(df, artist, algorandom=False, verbose=False):
    """Selects a few images randomly with the same year as the input variable
    and measures accuracy of prediction"""
    # Pick three entries with the same year as that selected (or output nan)
    df_artist = df[df['artist_name']==artist]
    if len(df_artist) < 8:
        return np.nan
    # Set a few extra parameters
    db = None
    con = None
    do_db = None
    if algorandom:
        best_inds = random.sample(range(len(df)),4)
    else:
        # Choose random entries from the df_yr dataframe
        inner_inds = random.sample(range(len(df_artist)), 2)
        # Get the index value in the big dataframe of these df_yr dataframe entries
        good_inds = df_artist.iloc[inner_inds].index.tolist()
        print(df['artist_name'].iloc[good_inds])
        # Pick three entries with a random year (bad inds)
        bad_inds = random.sample(range(len(df)),4)
        # Do the calculation
        best_inds = webapp.model.imgs_from_cats(good_inds, bad_inds, df, db, con, do_db, verbose=False)
    # Calculate how far dates of best inds are from the input year
    pred_years = np.zeros(len(best_inds))
    mse = 0.
    pred_artist = []
    for i, b in enumerate(best_inds):
        pred_artist.append(df['artist_name'].iloc[[b]].values[0])
        if verbose:
            print(pred_artist[i])
        if pred_artist[i] == artist:
            mse += 1
    return mse

def _validate_on_artist(df, artist, algorandom=False, verbose=False):
    """Selects a few images randomly with the same year as the input variable
    and measures accuracy of prediction"""
    # Pick three entries with the same year as that selected (or output nan)
    df_artist = df[df['artist_name']==artist].reset_index(drop=True)
    # Get only works by this artist if within 5 years of their median artwork year
    median_yr = df_artist['date'].median()
    year_filter = (df_artist['date'] - median_yr).abs()<5
    df_artist = df_artist[year_filter].reset_index(drop=True)
    if len(df_artist) < 8:
        return np.nan
    # Choose random entries from the df_yr dataframe
    inner_inds = random.sample(range(len(df_artist)), 3)
    # Get the index value in the big dataframe of these df_yr dataframe entries
    good_inds = df_artist.iloc[inner_inds].index.tolist()
    # Pick three entries with a random year (bad inds)
    bad_inds = random.sample(range(len(df)),3)
    # Set a few extra parameters
    db = None
    con = None
    do_db = None
    if algorandom:
        best_inds = random.sample(range(len(df)),4)
    else:
        best_inds = webapp.model.imgs_from_cats(good_inds, bad_inds, df, db, con, do_db, verbose=verbose)
    # Calculate how far dates of best inds are from the input year
    pred_years = np.zeros(len(best_inds))
    mse = 0.
    if verbose:
        print('median year = {:.1f}'.format(median_yr))
    for i, b in enumerate(best_inds):
        pred_years[i] = df['date'].iloc[[b]].values[0]
        if verbose:
            print(pred_years[i])
        mse += np.abs(pred_years[i] - median_yr)
    mse = mse / len(best_inds)
    return mse


def validate_on_year():
    df = pd.read_pickle('./webapp/webapp/static/art_yr_label_cln2_cats_labs_sparse.pickle')
    # Limit to entries with year values
    df = df[df['date']>0].reset_index(drop=True)
    yrs = np.arange(1600, 1900)
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

def _validate_on_year(df, year, algorandom=False, verbose=False):
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
        best_inds = webapp.model.imgs_from_cats(good_inds, bad_inds, df, db, con, do_db, verbose=verbose)
    # Calculate how far dates of best inds are from the input year
    pred_years = np.zeros(len(best_inds))
    mse = 0.
    for i, b in enumerate(best_inds):
        pred_years[i] = df['date'].iloc[[b]].values[0]
        if verbose:
            print(pred_years[i])
        mse += np.abs(pred_years[i] - year)
    mse = mse / len(best_inds)
    return mse
