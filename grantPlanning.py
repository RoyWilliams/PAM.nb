import sys
import assign
import grants
import people
import transactions
import util
import matplotlib.pyplot as plt

class grants_people_assign():
#  Spending actual by Grant by Category by Month
#    transactions.expend[grant][category][imonth]
#
#  Salary FTE actual by Person and by Grant and by month
#    transactions.salary[person][grant][imonth]
#
#  Salary FTE forecast by Person and by Grant and by month 
#    assign.forecast_fte[person][grant][imonth]
#
#  Salary cost forecast by person and Grant and Month
#    gpa.person_costs[person][grant][imonth]


    def __init__(self, gr, pe, an, tr, run):
        self.run = run
        self.grant_month  = gr.grants['month'] # 'spent' means at this month
        self.grants       = gr.grants['grants']
        self.people       = pe
        self.assign       = an
        self.transactions = tr
        self.person_costs = {}

        for grant in self.grants.keys():
            self.person_costs[grant] = {}
            for person in self.assign.forecast_fte.keys():
                if grant in self.assign.forecast_fte[person]:
                    gCost = [0.0]*run.nmonth
                    for imonth in range(run.nmonth):
                        fte = self.assign.forecast_fte[person][grant][imonth]
                        gCost[imonth] += fte * self.people.people[person]['fulltimeCost']
                    self.person_costs[grant][person] = gCost

    def html_grant_header(self, grant_name):
        g = self.grants[grant_name]
        out = '<div style="background-color:blue">&nbsp;</div>'
        out += '<h1>%s</h1>' % grant_name
        out += '%s (%s)<br/>' % (g['fullName'], g['projectId'])
        if 'start' in g:
            nmonth = util.getMonthIndex(g['end']) - util.getMonthIndex(g['start'])
            out += 'Start %s, End %s (%d months)<br/>' % (g['start'], g['end'], nmonth)
        out += 'As of %s<br/>' % self.grant_month
        if 'awarded' in g:
            out += '<table><tr><th>Category</th><th>Awarded</th><th>Spent</th></tr>'
            for category in util.categories():
                if category in g['awarded']:
                    aw = g['awarded'][category]
                else:
                    aw = 0
                if category in g['spent']:
                    sp = g['spent']  [category]
                else:
                    sp = 0
                out += '<tr><td>%s</td><td>%.0f</td><td>%.0f</td><tr/>' % (category, aw, sp)
            out += '</table>'
        return out


####### FORECAST SALARY
    def forecast_salary(self, grant_name):
        g = self.grants[grant_name]
        if not 'awarded' in g:
            return None
        if not 'Salary' in g['awarded']:
            return None
        awarded = g['awarded']['Salary']
        spent   = g['spent']['Salary']
        balance = awarded - spent

        persons = []
        for person in self.assign.forecast_fte.keys():
            if grant_name in self.assign.forecast_fte[person]:
                persons.append(person)

        forecast = {'persons': persons, 'records':[]}
        grant_end = util.getMonthIndex(g['end']) - self.run.istart
        last_month = min(grant_end, self.run.nmonth)

        for imonth in range(last_month):
            m_record = {}
            month = util.getMonthTxt(self.run.istart + imonth)
            m_record['month'] = month
            month_cost = 0
            ftes = []
            for person in persons:
                person_month_fte = self.assign.forecast_fte[person][grant_name][imonth]
                ftes.append(person_month_fte)
                person_month_cost = self.person_costs[grant_name][person][imonth]
                month_cost += person_month_cost
                spent      += person_month_cost
                balance    -= person_month_cost
            m_record['person_month_fte'] = ftes
            m_record['month_cost'] = month_cost
            m_record['spent']      = spent
            m_record['balance']    = balance
            forecast['records'].append(m_record)
        return forecast

    def html_forecast_salary(self, grant_name):
        forecast = self.forecast_salary(grant_name)
        if not forecast: return None

        out = '<h3>Forecast Salary</h3>'
        out += '<table border=1><tr><th>Month</th>'
        for person in forecast['persons']:
            out += '<th>' + person + '</th>'
        out += "<th>&nbsp;</th><th>Monthly</th><th>Cumulative</th><th>Balance</th>"
        out += '</tr>'

        fmt = '<td bgcolor="#dddddd">&nbsp;</td><td>%6.0f</td><td>%10.0f</td><td>%10.0f</td>'
        for m_record in forecast['records']:
            line = '<tr color=#0000ff><td>%s</td>' % m_record['month']
            pmfs = m_record['person_month_fte']
            for pmf in pmfs:
                if pmf > 0.005:
                    line += '<td>%9.0f%%</td>' % (100*pmf)
                else:
                    line += '<td></td>'
            line += fmt % (m_record['month_cost'],  m_record['spent'], m_record['balance'])
            line += '</tr>'
            out += line
        out += '</table>'
        return out

########## ACTUAL SALARY EXPENSE
    def actual_salary(self, grant_name):
        g = self.grants[grant_name]
        if not 'spent' in g or not 'Salary' in g['spent']:
            return None
        persons = []
        for person in self.people.people_name_set:
            if person in self.transactions.salary:
                if grant_name in self.transactions.salary[person]:
                    persons.append(person)

        actual = {'persons': persons, 'records':[]}
        spent = g['spent']['Salary']
        awarded = g['awarded']['Salary']
        balance = awarded - spent
        for imonth in range(self.run.nmonth):
            m_record = {}
            month = util.getMonthTxt(self.run.istart + imonth)
            m_record['month'] = month
            month_cost = 0
            ftes = []
            for person in persons:
                w = self.transactions.salary[person][grant_name][imonth]
                spent += w
                fte_cost = self.people.people[person]['fulltimeCost']
                person_actual_fte = w / fte_cost
                ftes.append(person_actual_fte)
                
                month_cost += w
                spent      += w
                balance    -= w

            m_record['person_month_fte'] = ftes
            m_record['month_cost'] = month_cost
            m_record['spent']      = spent
            m_record['balance']    = balance
            actual['records'].append(m_record)
        return actual

    def html_actual_salary(self, grant_name):
        g = self.grants[grant_name]
        actual = self.actual_salary(grant_name)
        if not actual: return None

        out = '<h3>Salary Spending</h3>'
        out += 'Grant <b>%s</b> (%s) <br/>Start %s, End %s' % (grant_name, g['projectId'], g['start'], g['end'])
        out += '<table border=1><tr><th>Month</th>'
        for person in actual['persons']:
            out += '<th>' + person + '</th>'
        out += "<th>&nbsp;</th><th>Monthly</th><th>Cumulative</th><th>Balance</th>"
        out += '</tr>'

        fmt = '<td bgcolor="#dddddd">&nbsp;</td><td>%6.0f</td><td>%10.0f</td><td>%10.0f</td>'
        for m_record in actual['records']:
            line = '<tr color=#0000ff><td>%s</td>' % m_record['month']
            pmfs = m_record['person_month_fte']
            for pmf in pmfs:
                if pmf > 0.005:
                    line += '<td>%9.0f%%</td>' % (100*pmf)
                else:
                    line += '<td></td>'
            line += fmt % (m_record['month_cost'],  m_record['spent'], m_record['balance'])
            line += '</tr>'
            out += line
        out += '</table>'
        return out

######### EXPENDITURE BY CATEGORY
    def actual_categories(self, grant_name):
        if grant_name not in self.transactions.expend:
            return None
        g = self.grants[grant_name]

        actual = {'categories': util.categories(), 'records':[]}
        for imonth in range(self.run.nmonth):
            m_record = {}
            month = util.getMonthTxt(self.run.istart + imonth)
            m_record['month'] = month
            costs = []
            for category in util.categories():
                if category in self.transactions.expend[grant_name]:
                    cost = self.transactions.expend[grant_name][category][imonth]
                else:
                    cost = 0.0
                costs.append(cost)
            m_record['costs'] = costs
            actual['records'].append(m_record)
        return actual

    def html_actual_categories(self, grant_name):
        g = self.grants[grant_name]
        actual = self.actual_categories(grant_name)
        if not actual or not 'start' in g:
            return None

        out = '<h3>Category Spending</h3>'
        out += 'Grant <b>%s</b> (%s) <br/>Start %s, End %s' % (grant_name, g['projectId'], g['start'], g['end'])
        out += '<table border=1><tr><th>Month</th>'
        for category in actual['categories']:
            out += '<th>' + category + '</th>'
        out += '</tr>'

        for m_record in actual['records']:
            line = '<tr color=#0000ff><td>%s</td>' % m_record['month']
            for cost in m_record['costs']:
                if cost > 0.005:
                    line += '<td>%9.0f</td>' % cost
                else:
                    line += '<td></td>'
            line += '</tr>'
            out += line
        out += '</table>'
        return out

    def plot_category(self, grant_name, category):
        g = self.grants[grant_name]
        actual = self.actual_categories(grant_name)
        if not actual or not 'start' in g:
            return None
        if not 'awarded' in g or not category in g['awarded']:
            return None
        icategory = actual['categories'].index(category)
        actual = actual['records']

        # spending at start of run and at end of grant
        trendspend = [g['spent'][category], g['awarded'][category]]
        grant_istart = util.getMonthIndex(g['start']) -1
        grant_iend   = util.getMonthIndex(g['end'])
        trendmonth = [grant_istart-self.run.istart, grant_iend-self.run.istart]
        plt.plot(trendmonth, trendspend, 'o-', markersize=15, color='gray')

        months = []
        ac = []
        cumulative = g['spent'][category]
        
        for imonth in range(self.run.nmonth):
            month = util.getMonthTxt(self.run.istart + imonth)
            months.append(month)
            cumulative += actual[imonth]['costs'][icategory]
            ac.append(cumulative)

        plt.plot(months, ac, 'o-', label='cumulative actual',   color='green')
        plt.axhline(0, color='black')
        plt.xticks(rotation=90)
        plt.xlabel("at end of month")
        plt.axis(xmin=0, xmax=self.run.nmonth)
        plt.axis(xmin=0)
#    plt.axis(        ymax=maxspend)
        plt.ylabel("cumulative spend")
        plt.legend(loc='upper left')
        plt.title(category + ' spending for ' + grant_name)

####### PLOT ACTUAL SALARY+Travel+Consumables
    def plot_actual_salary_travel_consumables(self, grant_name):
        actual_salary      = self.actual_salary(grant_name)
        actual_categories  = self.actual_categories(grant_name)
        if not actual_categories:
            return
        g = self.grants[grant_name]
        if not actual_salary or not 'start' in g:
            return
        if not 'awarded' in g:
            return None
        actual_salary     = actual_salary['records']
        actual_categories = actual_categories['records']

        # spending at start of run and at end of grant
        trendspend = [
            g['spent']  ['Salary'] + g['spent']  ['Travel'] + g['spent']  ['Consumables'], 
            g['awarded']['Salary'] + g['awarded']['Travel'] + g['awarded']['Consumables']
        ]
        grant_istart = util.getMonthIndex(g['start']) -1
        grant_iend   = util.getMonthIndex(g['end'])
        trendmonth = [grant_istart-self.run.istart, grant_iend-self.run.istart]
        plt.plot(trendmonth, trendspend, 'o-', markersize=15, color='gray')

        cumulative = g['spent']['Travel'] + g['spent']['Consumables']
        months = []
        ac = []
        for imonth in range(self.run.nmonth):
            month = util.getMonthTxt(self.run.istart + imonth)
            months.append(month)
            cumulative += actual_categories[imonth]['costs'][1] + actual_categories[imonth]['costs'][3]
            ac.append(actual_salary  [imonth]['spent'] + cumulative)

        plt.plot(months, ac, 'o-', label='cumulative actual',   color='red')
        plt.axhline(0, color='black')
        plt.xticks(rotation=90)
        plt.xlabel("at end of month")
        plt.axis(xmin=0, xmax=self.run.nmonth)
        plt.axis(xmin=0)
#    plt.axis(        ymax=maxspend)
        plt.ylabel("cumulative spend")
        plt.legend(loc='upper left')
        plt.title('Salary+travel+consumables for ' + grant_name)

#########  FORECAST FTE BY PERSON
    def forecast_fte_person(self, person):
        if not person in self.assign.forecast_fte:
            return None
        grant_names = sorted(self.assign.forecast_fte[person].keys())
        months = []
        for imonth in range(self.run.nmonth):
            month = util.getMonthTxt(self.run.istart + imonth)
            months.append(month)
        person_grants_fte = []
        colours = []
        for grant_name in grant_names:
            colours.append(self.grants[grant_name]['colour'])
            person_grant_fte = [0.0]*self.run.nmonth
            for imonth in range(self.run.nmonth):
                person_grant_fte[imonth] = self.assign.forecast_fte[person][grant_name][imonth]
            person_grants_fte.append(person_grant_fte)
        return {
            'grant_names':grant_names, 
            'months':months, 
            'colours':colours,
            'person_grants_fte':person_grants_fte}

######## ACTUAL FTE EXPENSES BY PERSON
    def actual_fte_person(self, person):
        if not person in self.transactions.salary:
            return None
        grant_names = sorted(self.transactions.salary[person].keys())
        fte_cost = self.people.people[person]['fulltimeCost']
        months = []
        for imonth in range(self.run.nmonth):
            month = util.getMonthTxt(self.run.istart + imonth)
            months.append(month)
        person_grants_cost = []
        colours = []
        for grant_name in grant_names:
            colours.append(self.grants[grant_name]['colour'])
            person_grant_cost = [0.0]*self.run.nmonth
            for imonth in range(self.run.nmonth):
                person_grant_cost[imonth] = \
                    self.transactions.salary[person][grant_name][imonth] / fte_cost
            person_grants_cost.append(person_grant_cost)
        return {
            'grant_names':grant_names, 
            'months':months, 
            'colours':colours,
            'person_grants_cost':person_grants_cost}

######## PLOT PERSON
    def plot_person(self, person):
        forecast = self.forecast_fte_person(person)
        actual   = self.actual_fte_person(person)
        plt.figure(figsize=(12,4))

        plt.subplot(1, 2,1)
        if forecast:
            tot = [0.0]*self.run.nmonth
            for igr in range(len(forecast['person_grants_fte'])):
                y = forecast['person_grants_fte'][igr]
                plt.bar(forecast['months'], y, bottom=tot, width=0.9, \
                    label=forecast['grant_names'][igr], color=forecast['colours'][igr])
                for imonth in range(self.run.nmonth):
                    tot[imonth] += y[imonth]
    
        plt.legend(loc='upper left')
        plt.xticks(rotation=90)
        plt.ylim((0.0,1.4))
        plt.xlabel("FTE charged")
        plt.xlabel("charged at end of month")
        plt.title("Cost forecast for " + person)

        plt.subplot(1, 2,2)
        if actual:
            tot = [0.0]*self.run.nmonth
            for igr in range(len(actual['person_grants_cost'])):
                y = actual['person_grants_cost'][igr]
                plt.bar(actual['months'], y, bottom=tot, width=0.9, \
                    label=actual['grant_names'][igr], color=actual['colours'][igr])
                for imonth in range(self.run.nmonth):
                    tot[imonth] += y[imonth]
    
            plt.legend(loc='upper left')
            plt.xticks(rotation=90)
            plt.ylim((0.0,1.4))
            plt.xlabel("FTE charged")
            plt.xlabel("charged at end of month")
            plt.title("Actual cost for " + person)

        plt.show()


####### PLOT FORECAST and ACTUAL SALARY
    def plot_forecast_actual_salary(self, grant_name):
        forecast = self.forecast_salary(grant_name)
        actual = self.actual_salary(grant_name)
        g = self.grants[grant_name]
        if not forecast or not actual or not 'start' in g:
            return
        forecast = forecast['records']
        actual = actual['records']

        # spending at start of run and at end of grant
        trendspend = [g['spent']['Salary'], g['awarded']['Salary']]
        grant_istart = util.getMonthIndex(g['start']) -1
        grant_iend   = util.getMonthIndex(g['end'])
        trendmonth = [grant_istart-self.run.istart, grant_iend-self.run.istart]
        plt.plot(trendmonth, trendspend, 'o-', markersize=15, color='gray')

        months = []
        fc = []
        ac = []
        for imonth in range(len(forecast)):
            month = util.getMonthTxt(self.run.istart + imonth)
            months.append(month)
            fc.append(forecast[imonth]['spent'])
            ac.append(actual  [imonth]['spent'])

        plt.plot(months, fc, 'o-', label='cumulative forecast', color='blue')
        plt.plot(months, ac, 'o-', label='cumulative actual',   color='red')
        plt.axhline(0, color='black')
        plt.xticks(rotation=90)
        plt.xlabel("at end of month")
        plt.axis(xmin=0, xmax=self.run.nmonth)
        plt.axis(xmin=0)
#    plt.axis(        ymax=maxspend)
        plt.ylabel("cumulative spend")
        plt.legend(loc='upper left')
        plt.title('Salary forecast/actual for ' + grant_name)

if __name__ == '__main__':
    import settings
    run = util.run('Aug-22', 'Apr-23')
    gr = grants.grants            (settings.MYGRANTS)
    gr.from_projects              (settings.PROJECTS, settings.PROJECTS_DATE)
    pe = people.people            (settings.PEOPLE)
    an = assign.assign            (settings.ASSIGN, gr, pe, run)
    tr = transactions.transactions(settings.TRANSACTIONS, gr, pe, run)

    gpa = grants_people_assign(gr, pe, an, tr, run)

    print('\nHeader')
    q = gpa.html_grant_header('Venice')
    print(q)

    print('\nForecast Salary')
    q = gpa.forecast_salary('Venice')
    print(q)

    print('\nHTML Forecast Salary')
    q = gpa.html_forecast_salary('Venice')
    print(q)

    print('\nActual Salary')
    q = gpa.actual_salary('Venice')
    print(q)

    print('\nHTML Actual Salary')
    q = gpa.html_actual_salary('Venice')
    print(q)

    print('\nCategory Spending')
    q = gpa.actual_categories('Venice')
    print(q)

    print('\nHTMLCategory Spending')
    q = gpa.html_actual_categories('Venice')
    print(q)

    print('\nForecast FTE person')
    q = gpa.forecast_fte_person('Bloggs')
    print(q)

    print('\nActual FTE person')
    q = gpa.actual_fte_person('Bloggs')
    print(q)
    
