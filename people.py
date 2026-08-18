import sys, json
import util

class people():
    def __init__(self, people_filename, run):
        try:
            data = json.loads(open(people_filename).read())
        except Exception as e:
            print('Error with people file: %s' % str(e))
            return
    
        self.run = run
        self.people = {}
        self.forecast_cost = {}
        for costChange in data:
            person      = costChange[0]
            staffNumber = costChange[1]
            date        = costChange[2]
            FTEcost     = costChange[3]
            if person in self.people:
                if staffNumber != self.people[person]['staffNumber']:
                    err = 'ERROR: %s has multiple staff numbers %d and %d'
                    err = err % (person, staffNumber, self.people[person]['staffNumber'])
                    print(err)
            else:
                self.people[person] = { 'staffNumber': staffNumber }

            from_month = util.getMonthIndex(date) - run.istart
            this_forecast_cost   = float(FTEcost) / 12   # monthly
            if not person in self.forecast_cost.keys():
                self.forecast_cost[person] = [0.0]*(run.nmonth)
            for imonth in range(max(0, from_month), run.nmonth):
                self.forecast_cost[person][imonth] = this_forecast_cost

        self.people_name_set = list(self.people.keys())
                
    def print(self):
        print('Monthly cost per full-time person\n')
        print('Each line is: Name, staffNUmber, Cost per month at start and end of run')
        for person in self.people.keys():
            staffNumber = self.people[person]['staffNumber']
            month0 = util.getMonthTxt(self.run.istart)
            cost0 = self.forecast_cost[person][0]
            month1 = util.getMonthTxt(self.run.istart + self.run.nmonth-1)
            cost1 = self.forecast_cost[person][self.run.nmonth-1]
            print('%15s %6d %7s £%5.0f to %7s £%5.0f' % \
                (person, staffNumber, month0, cost0, month1, cost1))

    def all_names(self):
        return list(self.people.keys())

    def set_names(self, person_set):
        self.people_name_set = person_set
        print('Restricting attention to ', self.people_name_set)

##########
if __name__ == '__main__':
    import settings
    run = util.run('Aug-22', 'Apr-23')
    pe = people(settings.PEOPLE, run)
    pe.print()
