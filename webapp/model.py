import numpy as np
import pandas as pd

def final_imgs(good_inds, bad_inds, q, df, db, con):
    #Get years of all artworks
    sql_query = "SELECT date FROM artworks;"
    allyrs = pd.read_sql_query(sql_query, con)
    # Find mean year of selected works
    mean_year = allyrs['date'].iloc[good_inds].mean()
    # mean_year = df['date'].iloc[good_inds].mean()
    # convert to numpy
    yrs = allyrs['date'].values
    yrinds = np.argsort(np.abs(yrs - mean_year))
    best_inds = yrinds[:4]
    print(mean_year)
    # print(df['date'].iloc[bad_inds].mean())
    # print(df['date'].iloc[[best_inds[0],best_inds[1],best_inds[2],best_inds[3]]])
    return best_inds
