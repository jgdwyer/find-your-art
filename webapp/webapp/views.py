from flask import render_template
from flask import request
from webapp import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
from a_Model import ModelIt
# from flask.ext.wtf import Form
# from wtforms.fields import RadioField

# user = 'jgdwyer'
# host = 'localhost'
# dbname = 'birth_db'
# db = create_engine('postgres://{:s}{:s}/{:s}'.format(user, host, dbname))
# con = None
# con = psycopg2.connect(database=dbname, user=user)

# SECRET_KEY = "development"

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

# class SimpleForm(Form):
#     example = RadioField('Label', choices=[('value','description'),('value_two','whatever')])

# @app.route('/')
# @app.route('/index')
# def index():
#     user = {'nickname': 'Miguel'}  # fake user
#     return render_template('index.html', title='Home', user=user, photo1=photo1)

# @app.route('/db')
# def birth_page():
#     sql_query = """
#                 SELECT * FROM birth_data_table WHERE delivery_method='Cesarean';
#                 """
#     query_results = pd.read_sql_query(sql_query, con)
#     births = ""
#     for i in range(10):
#         births += query_results.iloc[i]['birth_month']
#         births += "<br>"
#     return births
#
# @app.route('/db_fancy')
# def cesareans_page_fancy():
#     sql_query = """
#                 SELECT index, attendant, birth_month FROM birth_data_table WHERE delivery_method='Cesarean';
#                 """
#     query_results = pd.read_sql_query(sql_query, con)
#     births = []
#     for i in range(query_results.shape[0]):
#         births.append(dict(index=query_results.iloc[i]['index'],
#                            attendant=query_results.iloc[i]['attendant'],
#                            birth_month=query_results.iloc[i]['birth_month']))
#     return render_template('cesareans.html', births=births)




# @app.route('/1')
# def cesareans_input():
#     return render_template("1.html")
#
# @app.route('/2')
# def cesareans_input():
#     return render_template("1.html")
#
# @app.route('out')
# def cesareans_input():
#     return render_template("out.html")


  #pull 'birth_month' from input field and store it
  # patient = request.args.get('birth_month')
  # foo1=True

  # print(patient)
  # patient = request.form['maybe']
  # print(patient)
  # patient = request.form['no']
  # print('fooa')
  # print(patient)
  # print('foob')
  # patient = 'option1'
  # # Get which images the user clicked on
  # # Talk to database
  # # Do Calculations
  # # Spit out next images
  # if patient=='option1':
  #     img1=starfish
  # else:
  #     img1=baberuth
  # img2=''
  # img3=''
  # img4=''
    #just select the Cesareans  from the birth dtabase for the month that the user inputs
  # query = "SELECT index, attendant, birth_month FROM birth_data_table WHERE delivery_method='Cesarean' AND birth_month='%s'" % patient
  # print(query)
  # query_results=pd.read_sql_query(query,con)
  # print(query_results)
  # births = []
  # the_result = ''
  # for i in range(query_results.shape[0]):
  #     births.append(dict(index=query_results.iloc[i]['index'],
  #                        attendant=query_results.iloc[i]['attendant'],
  #                        birth_month=query_results.iloc[i]['birth_month']))
  #     the_result = ''
  #     the_result = ModelIt(patient, births)
  # return render_template("output.html", births = births, the_result = the_result)
  # return render_template("a.html", img1=img1)


# @app.route('/output')
# def cesareans_output():
#     return render_template("output.html")

# @app.route('/output', methods=['POST'])
# def cesareans_output():
#   #pull 'birth_month' from input field and store it
#   # patient = request.args.get('birth_month')
#   patient = request.form['birth_month']
#     #just select the Cesareans  from the birth dtabase for the month that the user inputs
#   query = "SELECT index, attendant, birth_month FROM birth_data_table WHERE delivery_method='Cesarean' AND birth_month='%s'" % patient
#   print(query)
#   query_results=pd.read_sql_query(query,con)
#   print(query_results)
#   births = []
#   the_result = ''
#   for i in range(query_results.shape[0]):
#       births.append(dict(index=query_results.iloc[i]['index'],
#                          attendant=query_results.iloc[i]['attendant'],
#                          birth_month=query_results.iloc[i]['birth_month']))
#       the_result = ''
#       the_result = ModelIt(patient, births)
#   return render_template("output.html", births = births, the_result = the_result)
