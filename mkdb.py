import pickle
import cln
from sqlalchemy import create_engine
import pandas as pd
import psycopg2
import getpass

def store_db(df):
    """ From command line in proper environment, first run:
    $ createdb art_3
    $ psql art_3
    """
    user = getpass.getuser()
    df['date'] = cln.convert_year(df['date'], debug=False)
    engine = create_engine('postgresql://' + user + ':1234@localhost/art_3')
    print(engine.url)
    df.to_sql('artworks', engine, if_exists='replace')


def separate_db_and_pd():
    df_file = 'art_yr_label_cln2_cats_labs_sparse_cln.pickle'
    df = pd.read_pickle('./dfs/' + df_file)
    # Create new dense dataframe with non-features
    df_dense = df.to_dense()
    # Get sparse feature column labels
    # Last line is to remove a bad category that somehow is still in there
    collabels = [col for col in list(df) if ((col.startswith('catbin:') or
                                              col.startswith('labbin:')) and
                                              not col=='catbin: ')]
    # Only store sparse features in a dataframe
    df_sparse = df[collabels]
    # Save as pickle
    df_sparse.to_pickle('./dfs/art_yr_label_cln2_cats_labs_sparse_cln_featuresonly.pickle')
    # Now remove sparse features from "dense" dataframe
    df_dense.drop(collabels, axis=1, inplace=True)
    # A peculiarity of the particular df file is that there are bad columns
    if df_file == 'art_yr_label_cln2_cats_labs_sparse_cln.pickle':
        df_dense.drop('level_0', axis=1, inplace=True)
        df_dense.drop('index', axis=1, inplace=True)
    # Store dense dataframe w/o features in database
    store_db(df_dense)
    df_dense.to_pickle('./dfs/art_yr_label_cln2_cats_labs_sparse_cln_nofeats.pickle')
