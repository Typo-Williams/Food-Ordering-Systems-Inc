from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_ordering.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = b'_asdjf&alskdj50asf890asd8f09]/'
db = SQLAlchemy(app)

from routes import *

if __name__ == '__main__':
    app.run(debug=True)

