import numpy as np
import pandas as pd

def final_imgs(good_inds, bad_inds, q, df, db, con, do_db):
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

def imgs_from_cats(good_inds, bad_inds, q, df, db, con, do_db):
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
