import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
import sklearn.metrics
import time
import random

def two_inds_per_cluster(con):
    """The initial quasi-random images presented to user-select
    Returns 36 index values with two values from each of the 18 clusters"""
    rand_inds = []
    # Loop over clusters
    for i in range(18):
        qry = pd.read_sql_query('SELECT index FROM artworks ' +
                                'WHERE cluster={:d}'.format(i), con)
        # Store index vals for this cluster as a 1-d numpy array
        index_vals = np.squeeze(np.array(qry.values))
        np.random.shuffle(index_vals)  # shuffles in place
        index_vals = list(index_vals[:2]) # and get two values
        # Get index values from many dataframe
        rand_inds = rand_inds + index_vals
    # Shuffle the random inds so that cluster 0 doesn't always appear first
    np.random.shuffle(rand_inds)
    return rand_inds

def append_random_imgs(rand_inds, con, session):
    """Given a list of index values and a database connection, return a list of
       url strings to the images and the updated session variable"""
    img = []
    sql_query_pre = "SELECT url_to_thumb FROM artworks WHERE index="
    for i, rand_ind in enumerate(rand_inds):
        # Set the session index value (could also use a GLOBAL variable here)
        session['rnd_ind' + str(i)] = str(rand_ind)
        # Call database to get urls of thumbnail images from index value
        sql_query = sql_query_pre + str(rand_ind) + ";"
        thumb_url_np = pd.read_sql_query(sql_query, con)
        # Add url string to list
        img.append(thumb_url_np.values[0][0])
    return img, session


def get_similar_art(good_inds, bad_inds, df_features, df_feat_sqd):
    """Given index of images a user likes and does not like, return the most
    similar!
      inputs:
       --good_inds - list of indices of artwork the user selected
       --bad_inds - list of indices of artwork the user did not select
       --df_features - pandas dataframe of features alone
       --df_feat_sqd -- pandas series of squared category values
      returns:
       --best_inds - list of 4 indices of most similar artwork
       --top_features - list of features that the user most liked"""
    # Calculate user profile
    user_vec = get_user_vector(good_inds, bad_inds, df_features)
    # Computer pairwise distance and convert to a N_samples x 1 vector
    # The none is there b/c scikit learn wants to represent that there is one sample
    distance = sklearn.metrics.pairwise.euclidean_distances(\
        df_features, user_vec, X_norm_squared=df_feat_sqd[:, None])
    # Convert from an N_samples x 1 to a 1-d N_samples array
    distance = np.squeeze(distance)
    #Get user top categories
    top_features = top_user_features(df_features, user_vec)
    # Remove any indices that we initially showed the user - no dupliates!
    distance = remove_init_results(distance, good_inds, bad_inds)
    # Sort in ascending order and get top four results
    best_vals = np.sort(distance)[:4]
    best_inds = np.argsort(distance)[:4]
    return best_inds, top_features


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


def top_user_features(df_features, user_vec, debug=True):
    """Given a user vector, calculate the features that the user liked most
      inputs:
        --df_features -- features only pandas dataframe
        --user_vec -- 1-d array of N_art of how much the user liked each
        --debug -- boolean of whether to print top 30 thing user liked/disliked
      returns:
        -- list of features (strings) that the user liked most"""
    # Force user vector as an N_art x 1 array
    user_vec = np.squeeze(user_vec.T)
    best_feature_scr = np.sort(user_vec)[::-1][:30]
    best_feature_ind = np.argsort(user_vec)[::-1][:30]
    if debug:
        # Print favorite features
        print('User likes-----')
        for ind, scr in zip(best_feature_ind, best_feature_scr):
            print(df_features.columns[ind] + '...{:.2f}'.format(scr))
        # Calculate least favorite features
        worst_feature_scr = np.sort(user_vec)[:30]
        worst_feature_ind = np.argsort(user_vec)[:30]
        # Print least favorite features
        print('User does not like-----')
        for ind, scr in zip(worst_feature_ind, worst_feature_scr):
            print(df_features.columns[ind] + '...{:.2f}'.format(scr))
    # Get a lits of top features to return to the webapp
    top_features = []
    # These features are helpful for the algorithm, but not helpful for the user
    uninformative_features = ['labbin:art', 'labbin:painting', 'labbin:drawing',
                              'labbin:illustration', 'labbin:sketch',
                              'labbin:picture frame']
    # Loop over top 30 features
    for ind, scr in zip(best_feature_ind, best_feature_scr):
        feature = df_features.columns[ind]
        if feature not in uninformative_features and scr > 1:
            # Remove the labbin: or catbin: part of the string
            top_features.append(feature[7:])
    # Get more features if we only less than three
    if len(top_features)<3:
        top_features = []
        for ind, scr in zip(best_feature_ind, best_feature_scr):
            feature = df_features.columns[ind]
            # But now say that the score just has to be greater than 0
            if feature not in uninformative_features and scr > 0:
                top_features.append(feature[7:])
        # Limit to five features chosen this way
        top_features = top_features[:5]
    return top_features


def remove_init_results(distance, good_inds, bad_inds):
    """Since we don't want to return the results we showed initially,
       set them to nan"""
    distance[good_inds] = np.nan
    distance[bad_inds] = np.nan
    return distance


def m_metric(artist, good_inds, bad_inds, df, df_cols, metric, bad_weight):
    """Script to do validation using different distance measures
       See validate_algo functions
         inputs:
          --metric: 'cosine', 'cityblock', euclidean'
          --bad_weight: 0, 0.1, 1
         returns:
          --1 if matches original artist and 0 if not"""
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
