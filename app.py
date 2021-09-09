from flask import Flask, render_template, request, url_for
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plotter


app = Flask(__name__, template_folder="templates")

@app.route("/home")
def test():
    print("Testing Testing")
    return "Testing"


@app.route("/", methods=['GET'])
def home():
    return render_template("interestform.html")


@app.route("/result", methods=['POST', 'GET'])
def provide_time():
    if request.method == 'POST':
        goal_type = str(request.form['goal_type'])
        int_rate = int(request.form['interest_rate'])
        starting_balance = int(request.form['starting_value'])
        monthly_cont = int(request.form['monthly_cont'])
        additional_cont = int(request.form['additional_cont'])
        goal = int(request.form['goal_amount'])
        calc = Calc(starting_balance, int_rate, monthly_cont, additional_cont,goal_type, goal)
        answer = calc.goal_type_handler()
        interest_and_cont = calc.contribution_vs_interest(answer[0])
        plot = calc.create_chart_by_year(answer[1])
        return render_template('formresult.html', starting_value=starting_balance, int_rate=int_rate,
                               monthly_cont=monthly_cont, additional_cont=additional_cont, goal=goal,
                               goal_reached=answer[0], interest_earned=interest_and_cont[0], total_cont=interest_and_cont[1])



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
        contributions = number_of_months * self.monthly_cont
        interest_earned = self.goal - contributions
        interest_and_cont = [interest_earned, contributions]
        return interest_and_cont

    def amount_at_goal_year(self):
        time = self.goal - 2021
        for i in range(0, time):
            self.calc_balance_by_year()
        return self.cur_balance

    def years_to_goal_income(self):
        nest_egg_needed = self.goal * 25
        self.goal = nest_egg_needed
        return self.years_to_goal()

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