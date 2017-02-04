from flask import Flask
app = Flask(__name__)
app.secret_key = '0.1590535asf100407506A'
from webapp import views
