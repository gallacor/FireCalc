from flask import Flask
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plotter
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from datetime import datetime

app = Flask(__name__, template_folder="templates")

# the name of the database; add path if necessary
db_name = 'retirementplans.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)


# Create UserPlan table
class UserPlan(db.Model):
    __tablename__ = 'user_plans'
    plan_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String)
    starting_bal = db.Column(db.Integer)
    cur_balance = db.Column(db.Integer)
    int_rate = db.Column(db.Integer)
    monthly_cont = db.Column(db.Integer)
    extra_cont = db.Column(db.Integer)
    goal = db.Column(db.Integer)
    interest_earned = db.Column(db.Integer)
    goal_type = db.Column(db.Integer)
    total_contributions = db.Column(db.Integer)
    years_to_retire = db.Column(db.String)
    time_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, calc):
        self.starting_bal = calc.starting_bal
        self.cur_balance = calc.starting_bal
        self.int_rate = calc.int_rate
        self.monthly_cont = calc.monthly_cont
        self.extra_cont = calc.extra_cont
        self.goal = calc.goal
        self.interest_earned = calc.interest_earned
        self.goal_type = calc.goal_type
        self.total_contributions = calc.total_contributions
        self.years_to_retire = calc.result_calc



# Create User table
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
