import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
import sklearn.metrics
import time
import random

def m_metric(artist, good_inds, bad_inds, df, df_cols, metric, bad_weight):
    """metric: 'cosine', 'cityblock', euclidean', 'l1', l2'
       bad_weight: 0, 0.1, 1
       returns 1 if matches original artist and 0 if not"""
    if metric=='random':
        best_inds = random.sample(range(len(df)), 4)
    else:
        good_vec = df_cols.iloc[good_inds].sum()
        bad_vec = df_cols.iloc[bad_inds].sum()
        user_vec = good_vec - bad_weight*bad_vec
        # Change to a 1 x n_features vector
        user_vec = user_vec[:,None].T
        # Computer pairwise distance
        distance = sklearn.metrics.pairwise_distances(df_cols, user_vec, metric=metric)
        distance = np.squeeze(distance)
        distance = remove_init_results(distance, good_inds, bad_inds)
        # Sort ascending to get top results
        best_vals = np.sort(distance)[:4]
        best_inds = np.argsort(distance)[:4]
    # Now determine whether we got the artist
    score = 0
    for b in best_inds:
        pred_artist = df['artist_name'].iloc[[b]].values[0]
        if pred_artist == artist:
            score = 1
    return score

def remove_init_results(distance, good_inds, bad_inds):
    """Since we don't want to return the results we showed initially,
       set them to nan"""
    distance[good_inds] = np.nan
    distance[bad_inds] = np.nan
    return distance

def final_imgs(good_inds, bad_inds, df, db, con, do_db):
    #Get years of all artworks
    sql_query = "SELECT date FROM artworks;"
    if do_db:
        allyrs = pd.read_sql_query(sql_query, con)
        allyrs = allyrs['date']
    else:
        allyrs = df['date']
    # Find mean year of selected works
    mean_year = allyrs.iloc[good_inds].mean()
    # mean_year = df['date'].iloc[good_inds].mean()
    # convert to numpy
    yrs = allyrs.values
    yrinds = np.argsort(np.abs(yrs - mean_year))
    best_inds = yrinds[:4]
    print(mean_year)
    # print(df['date'].iloc[bad_inds].mean())
    # print(df['date'].iloc[[best_inds[0],best_inds[1],best_inds[2],best_inds[3]]])
    return best_inds

def imgs_from_cats(good_inds, bad_inds, df, db, con, do_db, verbose=False):
    if do_db:
        return None
    else:
        collabels = [col for col in list(df) if (col.startswith('catbin:') or \
                                                 col.startswith('labbin:'))]
        # Get all samples
        df_cols = df[collabels]
        good_vec = df_cols.iloc[good_inds].mean()
        bad_vec = df_cols.iloc[bad_inds].mean()
        user_vec = good_vec - 0.1*bad_vec
        # Change to a 1 x n_features vector
        user_vec = user_vec[:,None].T
        # Computer pairwise distance
        distance = sklearn.metrics.pairwise_distances(df_cols, user_vec, metric='cosine')
        distance = np.squeeze(distance)
        # Since we don't want to return the results we showed initially,
        # Set them to nan
        distance[good_inds] = np.nan
        distance[bad_inds] = np.nan
        best_vals = np.sort(distance)[:4]
        best_inds = np.argsort(distance)[:4]
        if verbose:
            print('The shortest distances are:')
            print(best_vals)
            print('The best inds are:')
            print(best_inds)
        for b in best_inds:
            if verbose:
                print('--Index {:d}: ({:s})\ncats: {:s}\nlabels: {:s}'.\
                    format(b, df['filename_nospaces'].iloc[[b]].values[0],
                              df['categories_cleaned'].iloc[[b]].values[0],
                              df['label_names_cleaned'].iloc[[b]].values[0]))
    return best_inds


def imgs_from_cats_old(good_inds, bad_inds, df, db, con, do_db):
    if do_db:
        return None
    else:
        collabels = [col for col in list(df) if col.startswith('catbin:')]
        good_vec = df[collabels].iloc[good_inds].mean()
        bad_vec = df[collabels].iloc[bad_inds].mean()
        user_vec = good_vec - 0.5*bad_vec
        print(user_vec.sort_values(ascending=True)[:10])
        print(user_vec.sort_values(ascending=False)[:10])
        # Loop over rows to find the closest match
        cat_mse = np.empty(len(df))
        cat_mse[:] = np.nan
        for i, row in df[collabels].iterrows():
            if df['categories_cleaned'].iloc[[i]].values[0] is None:
                continue
            if i in good_inds:
                continue
            if len(df['categories_cleaned'].iloc[[i]].values[0])>0:
                cat_mse[i]=(row - user_vec).apply(np.square).sum()
        print(np.sort(cat_mse[:10]))
        best_inds = np.argsort(cat_mse)[:4]
        for b in best_inds:
            print(df['categories_cleaned'].iloc[[b]])
        return best_inds
