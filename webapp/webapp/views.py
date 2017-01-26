from flask import render_template
from flask import request, session
from webapp import app
# from sqlalchemy import create_engine
# from sqlalchemy_utils import database_exists, create_database
# import psycopg2
from model import final_imgs
import pandas as pd
import numpy as np
from webapp.settings import APP_STATIC
import os

penguin = 'https://upload.wikimedia.org/wikipedia/commons/0/07/Emperor_Penguin_Manchot_empereur.jpg'
# penguin = './Emperor_Penguin_Manchot_empereur.jpg'
starfish = 'https://upload.wikimedia.org/wikipedia/commons/0/0d/Starfish.jpg'
baberuth = 'https://upload.wikimedia.org/wikipedia/commons/0/09/Babe_Ruth_circa_1920.jpg'

# The number of images to show
N = 6
# Load the pandas dataframe
df = pd.read_pickle(os.path.join(APP_STATIC,'art_a_clean.pickle'))


@app.route('/')
@app.route('/index')
def index():
    # Get 6 random values
    rand_inds = np.arange(len(df))
    np.random.shuffle(rand_inds)  # shuffles in place
    rand_inds = list(rand_inds[:N])  # convert to list and limit to N entries
    # Store each random image index as a value in the sessions dictionary
    # Note that indices are stored as strings
    for i, rand_ind in enumerate(rand_inds):
        session['rnd_ind' + str(i)] = str(rand_ind)
    # Get urls of thumbnail images
    img = [df['url_to_thumb'][i] for i in rand_inds]
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
    best_inds = final_imgs(good_inds, bad_inds, q, df)
    # Placeholder
    img = [df['url_to_thumb'][i] for i in best_inds]
    return render_template("a.html", img=img)
