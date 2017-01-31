from flask import render_template
from flask import request, session
from webapp import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
from model import final_imgs, imgs_from_cats
import pandas as pd
import numpy as np
from webapp.settings import APP_STATIC
import os

do_db = False
# The number of images to show
N = 6

db = None
con = None
df = None

if do_db:
    # Establish a connection with the PSQL database
    user = 'jgdwyer'
    pswd = '1234'
    host = 'localhost'
    dbname = 'art_2'
    db = create_engine('postgres://{:s}:{:s}@{:s}/{:s}'.format(user, pswd,
                                                              host, dbname))
    con = None
    con = psycopg2.connect(database=dbname, user=user, host=host, password=pswd)
else:
    # Load pandas dataframe
    df = pd.read_pickle(os.path.join(APP_STATIC, 'art_yr_label_cln2_cats_labs_sparse.pickle'))

@app.route('/')
@app.route('/index')
def index():
    # Get size of data base
    if do_db:
        qry = pd.read_sql_query('SELECT count(*) AS exact_count FROM artworks', con)
        N_rows = qry.values[0][0]
    else:
        N_rows = len(df)
    # Get 6 random values
    rand_inds = np.arange(N_rows)
    np.random.shuffle(rand_inds)  # shuffles in place
    rand_inds = list(rand_inds[:N])  # convert to list and limit to N entries
    # Store each random image index as a value in the sessions dictionary
    # Note that indices are stored as strings
    img = []
    sql_query_pre = "SELECT url_to_thumb FROM artworks WHERE index="
    for i, rand_ind in enumerate(rand_inds):
        session['rnd_ind' + str(i)] = str(rand_ind)
        # Get urls of thumbnail images
        sql_query = sql_query_pre + str(rand_ind) + ";"
        if do_db:
            thumb_url_np = pd.read_sql_query(sql_query, con)
            # Convert from pandas -> numpy -> string value
            img.append(thumb_url_np.values[0][0])
        else:
            img.append(df['url_to_thumb'][rand_ind])
    # Send to template page
    return render_template('index.html', img=img)


@app.route('/a', methods=['POST'])
def pagea():
    # Collect decisions from previous page
    q = 6*[None]
    rand_inds = 6*[None]
    good_inds = []
    bad_inds = []
    for i in range(6):
        rand_inds[i] = int(session.get('rnd_ind' + str(i), None))
        q[i] = int(request.form['q' + str(i)])
        if q[i]==1:
            good_inds.append(rand_inds[i])
        else:
            bad_inds.append(rand_inds[i])
    # Use information from these response and the original input images to
    # decide which are most similar
    # ------------ Run Model - Placeholder ------------ #
    # best_inds = final_imgs(good_inds, bad_inds, q, df, db, con, do_db)
    best_inds = imgs_from_cats(good_inds, bad_inds, q, df, db, con, do_db)
    print(best_inds)
    # ------------ Run Model - Placeholder ------------ #
    # Get thumbnail address for best images
    sql_query_pre = "SELECT url_to_thumb, url_to_im, source_html, filename_spaces " + \
        "FROM artworks WHERE index="
    imgout, glink, alink, hreslink = [], [], [], []
    for best_ind in best_inds:
        sql_query = sql_query_pre + str(best_ind) + ";"
        if do_db:
            results = pd.read_sql_query(sql_query, con)
            img.append(results['url_to_thumb'].values[0])
            glink.append('http://' + results['source_html'].values[0])
            hreslink.append(results['url_to_im'].values[0])
            alink.append(link_to_art_dot_com(results['filename_spaces'].values[0]))
        else:
            print(best_ind)
            imgout.append(df['url_to_thumb'].iloc[[best_ind]].values[0])
            glink.append('http://' + df['source_html'].iloc[[best_ind]].values[0])
            hreslink.append(df['url_to_im'].iloc[[best_ind]].values[0])
            alink.append(link_to_art_dot_com(df['filename_spaces'].iloc[[best_ind]].values[0]))
            print(imgout[-1])
    # img = [df['url_to_thumb'][i] for i in best_inds]
    # # Get links to google art page
    # glink = ['http://' + df['source_html'][i] for i in best_inds]
    # # Make links to art.com search
    # alink = [df['filename_spaces'][i] for i in best_inds]
    # alink = [val.replace(' - Google Art Project.jpg',"") for val in alink]
    # alink = [val.replace(" -","").replace(" ","%20") for val in alink]
    # aprefix = 'http://www.art.com/asp/search_do.asp/_/posters.htm?searchstring='
    # alink = [aprefix + val for val in alink]
    # # Get link to high-res version
    # hrlink = [df['url_to_im'][i] for i in best_inds]
    # print(hrlink)
    return render_template("a.html", imgout=imgout, glink=glink, alink=alink,
                           hreslink=hreslink)

def link_to_art_dot_com(alink):
    alink = alink.replace(' - Google Art Project.jpg',"")
    alink = alink.replace(" -","").replace(" ","%20")
    apre = 'http://www.art.com/asp/search_do.asp/_/posters.htm?searchstring='
    alink = apre + alink
    return alink
