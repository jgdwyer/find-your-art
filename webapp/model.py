import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
import sklearn.metrics
import time
import random


def get_similar_art(good_inds, bad_inds, df_features, df_pre2):
    """Given index of images a user likes and does not like, return the most
    similar!
      inputs:
       --good_inds - list of indices of artwork the user selected
       --bad_inds - list of indices of artwork the user did not select
       --df_features - pandas dataframe of features alone
       --df_pre2 -- pandas series of squared category values
      returns:
       --best_inds - list of 4 indices of most similar artwork
       --top_features - list of features that the user most liked"""

    # Calculate user profile
    user_vec = get_user_vector(good_inds, bad_inds, df_features)
    # Computer pairwise distance and convert to a N_samples x 1 vector
    # distance = sklearn.metrics.pairwise_distances(df_features, user_vec, metric='euclidean')
    # The none is there b/c scikit learn wants to represent that there is one sample
    distance = sklearn.metrics.pairwise.euclidean_distances(df_features, user_vec,
                                                            X_norm_squared=df_pre2[:,None])
    distance = np.squeeze(distance)
    #Get user top categories
    top_features = top_user_features(df_features, user_vec)
    # Remove any indices that we initially showed the user
    distance = remove_init_results(distance, good_inds, bad_inds)
    # Sort ascending to get top four results
    best_vals = np.sort(distance)[:4]
    best_inds = np.argsort(distance)[:4]
    #Measure similarity to each category
    most_similar_distance_features_to_user(df_features, best_inds, user_vec)
    return best_inds, top_features



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

def get_user_vector(good_inds, bad_inds, df_features):
    """Calculate user profile by summing over each user-chosen images
       returns 1xN_features vector"""
    # Get an N_features vector by summing over all images the user liked
    good_vec = df_features.iloc[good_inds].sum()
    # And sum over images the user did not like
    bad_vec = df_features.iloc[bad_inds].sum()
    # Simple difference seems to work quite well
    user_vec = good_vec - 0.1*bad_vec
    # Change this to a 1xN_features vector for distance calculations
    user_vec = user_vec[:,None].T
    return user_vec

def top_user_features(df_features, user_vec):
    """Given a user vector, calculate the features that the user liked"""
    user_vec = np.squeeze(user_vec.T)
    best_feature_scr = np.sort(user_vec)[::-1][:30]
    best_feature_ind = np.argsort(user_vec)[::-1][:30]
    worst_feature_scr = np.sort(user_vec)[:30]
    worst_feature_ind = np.argsort(user_vec)[:30]
    print('User likes-----')
    for ind, scr in zip(best_feature_ind, best_feature_scr):
        print(df_features.columns[ind] + '...{:.2f}'.format(scr))
    print('User does not like-----')
    for ind, scr in zip(worst_feature_ind, worst_feature_scr):
        print(df_features.columns[ind] + '...{:.2f}'.format(scr))
    # Get a lits of top features to return to the webapp
    top_features = []
    uninformative_features = ['labbin:art', 'labbin:painting', 'labbin:drawing',
                              'labbin:illustration', 'labbin:sketch',
                              'labbin:picture frame']
    for ind, scr in zip(best_feature_ind, best_feature_scr):
        feature = df_features.columns[ind]
        if feature not in uninformative_features and scr > 1:
            top_features.append(feature[7:])
    top_features = set(top_features)
    if len(top_features)<3:
        top_features = []
        for ind, scr in zip(best_feature_ind, best_feature_scr):
            feature = df_features.columns[ind]
            if feature not in uninformative_features and scr > 0:
                top_features.append(feature[7:])
        top_features = top_features[:5]
    return top_features

def most_similar_distance_features_to_user(df_features, best_inds, user_vec):
    user_mat = np.diag(np.squeeze(user_vec.T))
    distance = np.zeros(len(df_features.columns))
    for b in best_inds:
        distance1 = sklearn.metrics.pairwise_distances(user_mat,
                                                      df_features.iloc[[b]],
                                                      metric='euclidean')
        distance += np.squeeze(distance1)
    cat_vals = np.sort(distance)[:20]
    cat_inds = np.argsort(distance)[:20]
    print(cat_vals)
    print(df_features.columns[cat_inds])


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
