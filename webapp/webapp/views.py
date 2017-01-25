from flask import render_template
from flask import request
from webapp import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from a_Model import ModelIt


penguin = 'https://upload.wikimedia.org/wikipedia/commons/0/07/Emperor_Penguin_Manchot_empereur.jpg'
# penguin = './Emperor_Penguin_Manchot_empereur.jpg'
starfish = 'https://upload.wikimedia.org/wikipedia/commons/0/0d/Starfish.jpg'
baberuth = 'https://upload.wikimedia.org/wikipedia/commons/0/09/Babe_Ruth_circa_1920.jpg'

@app.route('/')
@app.route('/index')
def index():
    user = [None]
    user[0] = 'Miguel'  # fake user
    img = 6*[None]
    img[0] = penguin
    img[1] = penguin
    img[2] = penguin
    img[3] = starfish
    img[4] = baberuth
    img[5] = starfish
    return render_template('index.html', img=img)


@app.route('/a', methods=['POST'])
def pagea():
    # Collect decisions from previous page
    q = 6*[None]
    for i in range(6):
        q[i] = int(request.form['q' + str(i)])
    # Use information from these response and the original input images to decide which are most similar
    return render_template("a.html", img1=img1)
