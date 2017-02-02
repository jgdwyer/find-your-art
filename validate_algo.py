import numpy as np
import pandas as pd
import webapp.model
import random
import time
import webapp.model as m

def validate_on_artist(verbose=False):
    df = pd.read_pickle('./webapp/webapp/static/art_yr_label_cln2_cats_labs_sparse.pickle')
    # Limit to entries with year values
    df = df[df['date']>0].reset_index(drop=True)
    collabels = [col for col in list(df) if (col.startswith('catbin:') or \
                                             col.startswith('labbin:'))]
    # Get all samples
    df_cols = df[collabels]
    artists = df['artist_name'].unique()
    # Loop over dataframe and calculate error from year
    score = np.empty((8, len(artists)))
    score[:] = np.nan
    for i, artist in enumerate(artists):
        if sum(df['artist_name']==artist) >= 7:
            score[:,i] = _validate_on_artist(df, df_cols, artist, verbose=verbose)
            print('Entry {:d} of {:d}, artist={:s}'.format(i, len(artists), artist))
            print('Score: ')
            print(score[:,i])
            print('Running tally: ')
            print(np.nansum(score, axis=1))
            print(sum(np.isfinite(score[0,:])))
    return score

def _validate_on_artist(df, df_cols, artist, verbose=False):
    """Selects a few images randomly with the same year as the input variable
    and measures accuracy of prediction"""
    # Pick three entries with the same year as that selected (or output nan)
    # It's important not to "reset_index" here!
    df_artist = df[df['artist_name']==artist]
    # Choose 2 random "good" entries from the df_yr dataframe
    inner_inds = random.sample(range(len(df_artist)), 2)
    # Get the index value in the big dataframe of these df_yr dataframe entries
    good_inds = df_artist.iloc[inner_inds].index.tolist()
    # Append 6 other random entries to list
    good_inds = good_inds + random.sample(range(len(df)), 4)
    # Pick 16 entries with a random year (bad inds)
    bad_inds = random.sample(range(len(df)), 16)
    # Initialize score
    score = np.empty(8)
    score[:] = np.nan
    # Evaluate different models
    score[0] = m.m_metric(artist, good_inds, bad_inds, df, df_cols, 'cosine', 0.1)
    score[1] = m.m_metric(artist, good_inds, bad_inds, df, df_cols, 'cosine', 0)
    score[2] = m.m_metric(artist, good_inds, bad_inds, df, df_cols, 'cosine', 1)
    score[3] = m.m_metric(artist, good_inds, bad_inds, df, df_cols, 'cityblock', 0.1)
    score[4] = m.m_metric(artist, good_inds, bad_inds, df, df_cols, 'euclidean', 0.1)
    score[5] = m.m_metric(artist, good_inds, bad_inds, df, df_cols, 'l1', 0.1)
    score[6] = m.m_metric(artist, good_inds, bad_inds, df, df_cols, 'l2', 0.1)
    score[7] = m.m_metric(artist, good_inds, bad_inds, df, df_cols, 'random', None)

    return score
