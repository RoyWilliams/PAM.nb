import sys, re
import grants
import people
import util
import settings
import pandas as pd

class transactions():
    def __init__(self, transaction_filename, gr, pe, run):
        self.gr = gr.grants
        self.pe = pe
        self.run = run

        projectId_to_shortName = {}
        for k,v in self.gr.items():
            projectId_to_shortName[v['projectId']] = k

        # Expenditure is on Sheet2
        sheet_name = 'Sheet2'
        tr = pd.read_excel(transaction_filename, sheet_name=sheet_name, skiprows=2)

        column_names = list(tr.columns.values)
        #print(column_names)
        project_id           = column_names.index('Project ID')
        expenditure_category = column_names.index('Expenditure Category')
        accounting_period    = column_names.index('Accounting Period')
        gbp_amount           = column_names.index('GBP Amount')
        comment              = column_names.index('Comment')

        n = len(tr.index)
        expend = {}
        salary = {}

        ns = util.nameSearcher(settings.PEOPLE)
    
        for i in range(n):
            row = tr.iloc[i]
            project  = row[project_id]
            if not isinstance(project, str):
                continue
            if len(project.split('_')) != 2:
                continue

            if project in projectId_to_shortName:
                grant = projectId_to_shortName[project]
            else:
                print('ERROR Unknown project Id %s!' % project)
                continue

            their_category = str(row[expenditure_category])
            category = util.my_category(their_category)
            if not category:
                continue
            
            imonth   = util.getMonthIndex(row[accounting_period]) - run.istart
            if imonth < 0 or imonth >= run.nmonth:
                continue
            amount   = float(row[gbp_amount])
            if amount < 0.1:
                continue
            if category == 'Salary':
                person = ns.findName(row[comment])
#                print('%s paid %f month %d' % (person, amount, imonth)) 
                if not person: 
                    print('ERROR: did not find known person in spreadsheet comment "%s"', row[comment])
                    continue

                if not person in salary: 
                    salary[person] = {}
                if not grant in salary[person]: 
                    salary[person][grant] = [0.0]*(run.nmonth)
                salary[person][grant][imonth] += amount

            if not grant in expend:
                expend[grant] = {}
            if not category in expend[grant]:
                expend[grant][category] = [0.0]*(run.nmonth)
            expend[grant][category][imonth] += amount

        self.expend = expend
        self.salary = salary

    def print_salary(self):
        for person in self.pe.people_name_set:
            print(person)
            if person not in self.salary:
                continue
            for grant in self.salary[person].keys():
                print('  ' + grant)
                for imonth in range(self.run.nmonth):
                    month = util.getMonthTxt(self.run.istart + imonth)
                    print('    %8s %12.0f' % (month, self.salary[person][grant][imonth]))

    def print_expend(self):
        for grant in self.gr.keys():
            print(grant)
            if grant not in self.expend:
                continue
            for category in self.expend[grant].keys():
                print('  ' + category)
                for imonth in range(self.run.nmonth):
                    month = util.getMonthTxt(self.run.istart + imonth)
                    print('    %8s %12.0f' % (month, self.expend[grant][category][imonth]))


if __name__ == "__main__":
    import settings
    run = util.run('Aug-22', 'Apr-23')
    gr = grants.grants    (settings.MYGRANTS, settings.GRANTS_DATE)
    pe = people.people    (settings.PEOPLE)
    tr = transactions     (settings.TRANSACTIONS, gr, pe, run)
    tr.print_salary()
    print('------')
    tr.print_expend()
