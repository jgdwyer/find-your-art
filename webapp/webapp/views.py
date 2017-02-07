from flask import render_template
from flask import request, session
from webapp import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import model
import pandas as pd
import numpy as np
from webapp.settings import APP_STATIC
import os
import getpass

do_db = True
# The number of images to show
N = 36

db = None
con = None
df = None

if do_db:
    # Establish a connection with the PSQL database
    user = getpass.getuser()
    pswd = '1234'
    host = 'localhost'
    dbname = 'art_3'
    db = create_engine('postgres://{:s}:{:s}@{:s}/{:s}'.format(user, pswd,
                                                              host, dbname))
    con = None
    con = psycopg2.connect(database=dbname, user=user, host=host, password=pswd)

    qry = pd.read_sql_query('SELECT count(*) AS exact_count FROM artworks', con)
    N_rows = qry.values[0][0]
else:
    # Load pandas dataframe
    df = pd.read_pickle(os.path.join(APP_STATIC, 'art_yr_label_cln2_cats_labs_sparse_cln_nofeats.pickle'))
    N_rows = len(df)

df_feat = pd.read_pickle(os.path.join(APP_STATIC, \
    'art_yr_label_cln2_cats_labs_sparse_cln_featuresonly.pickle'))
df_pre2 = pd.read_pickle(os.path.join(APP_STATIC, \
    'art_yr_label_cln2_cats_labs_sparse_cln_featuresonly_distance2.pickle'))

@app.route('/')
@app.route('/index')
def index():
    # Get 6 random values
    rand_inds = np.arange(N_rows)
    np.random.shuffle(rand_inds)  # shuffles in place
    rand_inds = list(rand_inds[:N])  # convert to list and limit to N entries
    print(rand_inds)
    # Store each random image index as a value in the sessions dictionary
    # Note that indices are stored as strings
    img, session = append_random_imgs(rand_inds, do_db, con, df)
    # Send to template page
    return render_template('index.html', img=img)


@app.route('/demo_seed')
def demo_seed():
    inds = [6352, 5121, 7332, 11110, 10679, 9802, 3105, 8820, 117, 12730, 6014, 1643, 433,
            4040, 5050, 2121, 7570, 12389, 3205, 7142, 898, 3190, 395, 9023,
             12162, 2502, 1350, 2276, 10198, 14156, 493, 13936, 6992, 774, 7422, 4412]
    img, session = append_random_imgs(inds, do_db, con, df)
    return render_template('index.html', img=img)


@app.route('/results', methods=['POST'])
def pagea():
    # Collect decisions from previous page
    print('pagea')
    # q = N*[0]
    rand_inds = N*[None]
    good_inds = []
    bad_inds = []
    for i in range(N):
        print('starting loop')
        rand_inds[i] = int(session.get('rnd_ind' + str(i), None))
    print('now getting formdata pre loop')
    # Need to use the getlist subroutine b/c form is returning multiple values
    qlist = request.form.getlist('q')
    #Check if list is empty
    if len(qlist)==0:
        error('Need to select at least one item')
    # Convert list entries to ints
    qlist = [int(q) for q in qlist]
    # Loop over all sample images and check if user selected them
    for i in range(N):
        if i in qlist:
            # Yes - user selected
            good_inds.append(rand_inds[i])
            print('good: ' + str(i))
        else:
            # No - user did not select
            bad_inds.append(rand_inds[i])
            print('bad: ' + str(i))

    # Use information from these response and the original input images to
    # decide which are most similar
    # ------------ Run Model -  ------------ #
    # best_inds = final_imgs(good_inds, bad_inds, df, db, con, do_db)
    best_inds, top_features = model.get_similar_art(good_inds, bad_inds, df_feat, df_pre2)
    # best_inds = imgs_from_cats(good_inds, bad_inds, df, db, con, do_db, verbose=False)
    print(best_inds)
    # ------------ Run Model -  ------------ #
    # Get thumbnail address for best images
    sql_query_pre = "SELECT url_to_thumb, url_to_im, source_html, filename_spaces " + \
        "FROM artworks WHERE index="
    imgout, glink, alink, hreslink, artwork_name = [], [], [], [], []
    for best_ind in best_inds:
        sql_query = sql_query_pre + str(best_ind) + ";"
        if do_db:
            results = pd.read_sql_query(sql_query, con)
            print(results)
            imgout.append(results['url_to_thumb'].values[0])
            glink.append('http://' + results['source_html'].values[0])
            hreslink.append(results['url_to_im'].values[0])
            alink.append(link_to_art_dot_com(results['filename_spaces'].values[0]))
            artwork_name.append(results['filename_spaces'].values[0].replace(' - Google Art Project.jpg',""))
        else:
            print(best_ind)
            imgout.append(df['url_to_thumb'].iloc[[best_ind]].values[0])
            glink.append('http://' + df['source_html'].iloc[[best_ind]].values[0])
            hreslink.append(df['url_to_im'].iloc[[best_ind]].values[0])
            alink.append(link_to_art_dot_com(df['filename_spaces'].iloc[[best_ind]].values[0]))
            artwork_name.append(df['filename_spaces'].iloc[[best_ind]].values[0].replace(' - Google Art Project.jpg',""))
    return render_template("out.html", imgout=imgout, glink=glink, alink=alink,
                           hreslink=hreslink, artwork_name=artwork_name,
                           top_features=top_features)

@app.route('/about')
def about():
   # Send to template page
   return render_template('about.html')

def append_random_imgs(rand_inds, do_db, con, df):
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
    return img, session

def link_to_art_dot_com(alink):
    alink = alink.replace(' - Google Art Project.jpg',"")
    alink = alink.replace(" -","").replace(" ","%20")
    apre = 'http://www.art.com/asp/search_do.asp/_/posters.htm?searchstring='
    alink = apre + alink
    return alink
