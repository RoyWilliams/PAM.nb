import sys
import grants
import people
import util
import pandas as pd

class transactions():
    def __init__(self, transaction_filename, people_filename, gr, run):
        self.gr = gr
        self.pe = pe = people.people(people_filename)
        self.run = run

        projectId_to_shortName = {}
        for k,v in gr.items():
            projectId_to_shortName[v['projectId']] = k

        sheet_name = 'Expenditure'
        tr = pd.read_excel(transaction_filename, sheet_name=sheet_name)
        n = len(tr.index)
        ns = util.nameSearcher(people_filename)
    
        expend = {}
        salary = {}
    
        for i in range(n):
            row = tr.iloc[i]
            project  = row[0]
            if not isinstance(project, str):
                continue
            if len(project.split('_')) != 2:
                continue

            if project in projectId_to_shortName:
                grant = projectId_to_shortName[project]
            else:
                print('ERROR Unknown project Id %s!' % project)
                continue

            their_category = str(row[3])
            category = util.my_category(their_category)
            if not category:
                continue
            
            imonth   = util.getMonthIndex(row[13]) - run.istart
            if imonth < 0 or imonth >= run.nmonth:
                continue
            amount   = float(row[14])
            if amount < 0.1:
                continue
            if category == 'Salary':
                person = ns.findName(row[19])
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
        for person in self.pe.persons:
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
    run = util.run('Aug-22', 'Apr-23')
    gr = grants.grants('data/grants.json')
    tr = transactions( 'data/transaction.xlsx', 'data/people.json', gr.grants['grants'], run)
    tr.print_salary()
    print('------')
    tr.print_expend()
