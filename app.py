from flask import Flask, render_template, request, url_for
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plotter
from flask_sqlalchemy import SQLAlchemy
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
    starting_bal = db.Column(db.Integer)
    cur_balance = db.Column(db.Integer)
    int_rate = db.Column(db.Float)
    monthly_cont = db.Column(db.Integer)
    extra_cont = db.Column(db.Integer)
    goal = db.Column(db.Integer)
    interest_earned = db.Column(db.Integer)
    goal_type = db.Column(db.String)
    total_contributions = db.Column(db.Integer)
    years_to_retire = db.Column(db.String)
    time_created = db.Column(db.DateTime, default = datetime.utcnow)

    def __init__(self, calc):
        self.starting_bal = calc.starting_bal
        self.cur_balance = calc.cur_balance
        self.int_rate = calc.int_rate
        self.monthly_cont = calc.monthly_cont
        self.extra_cont = calc.extra_cont
        self.goal = calc.goal
        self.interest_earned = round(calc.interest_earned, 2)
        self.goal_type = calc.goal_type
        self.total_contributions = calc.total_contributions
        self.years_to_retire = calc.result_calc[0]


db.create_all()

@app.route("/home")
def test():
    print("Testing Testing")
    return "Testing"


@app.route("/", methods=['GET'])
def home():
    return render_template("interestform.html")


@app.route("/view_database", methods=['GET', 'POST'])
def db_operations():
    if request.method == 'GET':
        return view_db()
    elif request.method == 'POST':
        if 'delete-btn' in request.form:
            return delete_plan()
        else:
            return update_plan_submit()

def delete_plan():
    plan_id = request.form['delete-btn']
    UserPlan.query.filter(UserPlan.plan_id == plan_id).delete()
    db.session.commit()
    rows = UserPlan.query.order_by(UserPlan.time_created)
    return render_template('view_db.html', rows=rows)


def update_plan_submit():
    plan_id = request.form['update-btn']
    plan_to_edit = UserPlan.query.filter(UserPlan.plan_id == plan_id).first()
    return render_template('updateplan.html', plan_to_edit = plan_to_edit)


def view_db():
    rows = UserPlan.query.order_by(UserPlan.time_created)
    return render_template('view_db.html', rows=rows)


@app.route('/updateplan', methods=['GET', 'POST'])

def update_plan():
        goal_type, int_rate = str(request.form['goal_type']), int(request.form['interest_rate'])
        starting_balance, monthly_cont = int(request.form['starting_value']), int(request.form['monthly_cont'])
        additional_cont,  goal = int(request.form['additional_cont']),  int(request.form['goal_amount'])
        updated_plan = Calc(starting_balance, int_rate, monthly_cont, additional_cont, goal_type, goal)

        #updatte attributtes of original_record
        plan_id = request.form['update-btn']
        plan_to_edit = UserPlan.query.filter(UserPlan.plan_id == plan_id)
        plan_to_edit.starting_bal = updated_plan.starting_bal
        plan_to_edit.cur_balance = updated_plan.cur_balance
        plan_to_edit.int_rate = updated_plan.int_rate
        plan_to_edit.monthly_cont = updated_plan.monthly_cont
        plan_to_edit.extra_cont = updated_plan.extra_cont
        plan_to_edit.goal = updated_plan.goal
        plan_to_edit.interest_earned = round(updated_plan.interest_earned, 2)
        plan_to_edit.goal_type = updated_plan.goal_type
        plan_to_edit.total_contributions = updated_plan.total_contributions
        plan_to_edit.years_to_retire = updated_plan.result_calc[0]
        db.session.commit()
        return view_db()










@app.route("/add_plan", methods=['POST', 'GET'])
def provide_time():
    if request.method == 'POST':
        #initialize variables and calc  object
        goal_type, int_rate = str(request.form['goal_type']), int(request.form['interest_rate'])
        starting_balance, monthly_cont = int(request.form['starting_value']), int(request.form['monthly_cont'])
        additional_cont,  goal = int(request.form['additional_cont']),  int(request.form['goal_amount'])
        calc = Calc(starting_balance, int_rate, monthly_cont, additional_cont,goal_type, goal)
        calc.create_chart_by_year(calc.result_calc[1])
        new_plan = UserPlan(calc)
        db.session.add(new_plan)
        db.session.commit()

        # return result page
        return render_template('formresult.html', starting_value=starting_balance, int_rate=int_rate,
                               monthly_cont=monthly_cont, additional_cont=additional_cont, goal=goal,
                               goal_reached=calc.result_calc[0], interest_earned=round(calc.interest_earned,2),
                               total_cont=calc.total_contributions)


class Calc:
    def __init__(self, starting_bal, int_rate, monthly_cont, extra_cont, goal_type, goal=0):
        self.starting_bal = starting_bal
        self.cur_balance = starting_bal
        self.int_rate = int_rate / 100 - .02
        self.monthly_cont = monthly_cont
        self.extra_cont = extra_cont
        self.goal = goal
        self.interest_earned = 0
        self.goal_type = goal_type
        self.total_contributions = 0
        self.result_calc = self.goal_type_handler()


    def goal_type_handler(self):
        if self.goal_type == "income":
            return self.years_to_goal_income()
        elif self.goal_type == "lump_sum":
            return self.years_to_goal()
        elif self.goal_type == "time":
            return self.amount_at_goal_year()

    def calc_monthly_stats(self):
        interest_prev_month = self.cur_balance * (self.int_rate / 12)
        self.interest_earned += round(interest_prev_month, 2)
        self.cur_balance = round(self.cur_balance + interest_prev_month + self.monthly_cont, 2)
        self.total_contributions += self.monthly_cont
        return [self.cur_balance, self.interest_earned, self.total_contributions]

    def calc_balance_by_year(self):
        #initialize variables
        bal_by_month = {}
        #calculate balance and interest each month
        for i in range(1,13):
            month_data = self.calc_monthly_stats()
            bal_by_month[i] = month_data
            if self.cur_balance >= self.goal:
                break
        self.cur_balance += self.extra_cont
        bal_by_month[12] = [self.cur_balance, self.interest_earned]
        # update cur_balance and interest_earned
        return bal_by_month, i

    def years_to_goal(self):
        cur_year = 2021
        bal_by_year = {}
        while self.cur_balance < self.goal:
            yearly_gain = self.calc_balance_by_year()
            bal_by_year[cur_year] = yearly_gain[0]
            #deals with case where goal is reached mid year
            if yearly_gain[1] < 12:
                cur_year += yearly_gain[1]/12
            else:
                cur_year += 1
        return str(round(cur_year - 2021, 2)), bal_by_year

    def contribution_vs_interest(self, time):
        """
        :return: interest earned and amount earned during the model
        """
        number_of_months = float(time) * 12
        self.total_contributions = number_of_months * self.monthly_cont
        self.interest_earned = round(self.goal - self.total_contributions, 2)

    def amount_at_goal_year(self):
        time = self.goal - 2021
        for i in range(0, time):
            self.calc_balance_by_year()
        return self.cur_balance

    def years_to_goal_income(self):
        nest_egg_needed = self.goal * 25
        self.goal = nest_egg_needed
        return self.years_to_goal()

    def add_to_csv(self):
        pass

    def create_chart_by_year(self, ending_data):
        if self.goal != 0:
            timeline = ending_data
            #need to dealwith amount_at_goal_year function
            years = [x for x in timeline.keys()]
            values = [x for x in timeline.values()]
            yearly_balances, total_balances, interest_balances, contribution_balances = [], [], [], []
            for year in values:
                yearly_balances.append(year[1])
            # create lists of interest and contribution over time
            i = 0
            while i <= 2:
                for year in yearly_balances:
                    if i == 0:
                        total_balances.append(year[i])
                    elif i == 1:
                        interest_balances.append(round(year[i], 2))
                    else:
                        contribution_balances.append(year[i])
                i += 1
            #create plot and save to file
            # plotter.stackplot(years, contribution_balances, interest_balances)
            plotter.plot(years, contribution_balances)
            plotter.plot(years, interest_balances)
            plotter.plot(years, total_balances)
            plotter.legend(loc = 'upper left')
            plotter.title('Time to Retirement')
            plotter.xlabel('Year')
            plotter.ylabel("Total Retirement Savings")
            plotter.legend()
            plotter.savefig('static/retirement.jpg', bbox_inches='tight')
            plotter.clf()


if __name__ == '__main__':
    app.run(debug=True,
            port=9000)