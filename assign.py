import sys, json
import util

# Reads the file that assigns peoples FTE to grants. 
# The file has the form of records like this
#     ["Davidson",    "Gaia21To22",    "Jan-22",    0.5],
# which says that from the beginning on Jan-22, Davidson is employed 
# by grant Gaia21To22 at 50%. It is assumed to continue at this rate until reset.
# You can run the code by itself to see what happens.

# make an array of actual FTE as self.forecast_fte[person][grant][i]
class assign():
    def __init__(self, assign_filename, grants, people, run):
        self.run = run
        self.pe = people
        self.gr = grants
        grant_names = self.gr.all_names()

        forecast_fte = {}
        records = json.loads(open(assign_filename, 'r').read())
        for record in records:
            person  = record[0]
            if not person in self.pe.all_names():
                print('ERROR: name %s in assign file not recognised' % person)
                continue
            grant = record[1]
            if not grant in self.gr.all_names():
#                print('ERROR: grant %s in assign file not recognised' % grant)
                continue
            from_month = util.getMonthIndex(record[2]) - run.istart
            this_forecast_fte   = float(record[3])
            if not person in forecast_fte:
                forecast_fte[person] = {}
            if not grant in forecast_fte[person]:
                forecast_fte[person][grant] = [0.0]*(run.nmonth)
            for imonth in range(max(0, from_month), run.nmonth):
                forecast_fte[person][grant][imonth] = this_forecast_fte
        self.forecast_fte = forecast_fte

    def print(self):
        for person in self.forecast_fte.keys():
            if not person in self.pe.people_name_set:
                continue
            print(person)
            for imonth in range(self.run.nmonth):
                month = util.getMonthTxt(self.run.istart + imonth)
                tot_forecast_fte = 0
                s = ''
                for grant in self.forecast_fte[person].keys():
                    forecast_fte = self.forecast_fte[person][grant][imonth]
                    if forecast_fte > 0:
                        s += '%4.2f on %10s| ' % (forecast_fte, grant)
                        tot_forecast_fte += forecast_fte
                print('   %s (%4.2f): %s' % (month, tot_forecast_fte, s))

if __name__=="__main__":
    import grants, people, settings
    run = util.run('Aug-22', 'Apr-23')
    gr = grants.grants(settings.MYGRANTS, settings.GRANTS_DATE)
    gr.from_projects  (settings.PROJECTS)
    pe = people.people(settings.PEOPLE)
    af = assign       (settings.ASSIGN, gr, pe, run)
    af.print()
