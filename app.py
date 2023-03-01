from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from socket import gethostname
from flask_login import current_user, LoginManager,login_user, logout_user,login_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_ordering.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = b'_asdjf&alskdj50asf890asd8f09]/'
db = SQLAlchemy(app)

from routes import *

if __name__ == '__main__':
    #create database
    #db.drop_all()
    #db.create_all()
    #check to see if it is running in pythonanywhere or not
    #this setting is recommended by pythonanywhere setup guide 
    # https://help.pythonanywhere.com/pages/Flask
    if 'liveconsole' not in gethostname():
        #app.run()
        app.run(debug=True)

