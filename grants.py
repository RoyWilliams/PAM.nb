import sys, json
import pandas as pd
import util

# Reads in a list of grants and their shortnames
# Can also read in financial information from the projects.xls file

class grants():
    def __init__(self, grants_filename):
        self.grants_filename = grants_filename
        self.grants = json.loads(open(grants_filename, 'r').read())
        self.grant_name_set = list(self.grants['grants'].keys())

    def from_projects(self, project_filename, month):
        mygr = self.grants['grants']
        projectId_to_shortName = {}
        for k,v in mygr.items():
            projectId_to_shortName[v['projectId']] = k

        # Now read the P&M file
        pam = pd.read_excel(project_filename)
    
        for index, row in pam.iterrows():
            project = row['Project Number']
            if project not in projectId_to_shortName:
                print('ERROR PaM projectID not in mygrants.json: %s - %s' % (project, row['Project Name']))
                continue

            shortName = projectId_to_shortName[project]
            grant = mygr[shortName]
        
            if not 'start'   in grant: 
                grant['start'] = util.dateTimeToMonthTxt(row['Project Start Date'])
            if not 'end'     in grant: 
                grant['end']   = util.dateTimeToMonthTxt(row['Project End Date'])
            if not 'awarded' in grant: grant['awarded'] = {}
            if not 'spent'   in grant: grant['spent'] = {}
    
            their_category = str(row['Resource'])
            category = util.my_category(their_category)
            if not category:
                continue
            awarded = float(row['Budget (GBP)'])
            if category in grant['awarded']: grant['awarded'][category] += awarded
            else:                            grant['awarded'][category]  = awarded

            spent   = float(row['Actual Expenditure (GBP)'])
            if category in grant['spent']: grant['spent'][category] += spent
            else:                          grant['spent'][category]  = spent

        # check that each mygrant was in the PAM report
        for shortName, gr in self.grants['grants'].items():
            if not 'awarded' in gr:
                print('WARNING: %s in mygrants not found in PAM file' % shortName)
            for category in util.categories():
                if not category in gr['awarded']:
                    gr['awarded'][category] = 0
                if not category in gr['spent']:
                    gr['spent'][category] = 0

        self.grants = {'month':month, 'grants':mygr}
        self.grant_name_set = mygr.keys()

    def print(self):

        if 'month' in self.grants:
            print('As of beginning of %s' % self.grants['month'])
        for shortName in self.grant_name_set:
            grant = self.grants['grants'][shortName]
            print('  P&M project ', grant['projectId'], shortName, grant['fullName'])
            
            if 'start' in grant:
                nmonth = util.getMonthIndex(grant['end']) - util.getMonthIndex(grant['start'])
                print('   Start %s, End %s (%d months)' % (grant['start'], grant['end'], nmonth))
            if 'awarded' in grant:
                print('   Awarded     Spent    Category')
                for category in util.categories():
                    print('%10.0f %10.0f   %s' % \
                    (grant['awarded'][category], grant['spent'][category], category))
            print()

    def write(self, filename):
        f = open(filename, 'w')
        f.write(json.dumps(self.grants, indent=2))
        f.close()

    def colour_chart(self):
        out = '<html>'
        div = '<div style="background-color:%s ; padding: 20px;">%s</div>\n'
        for shortName in self.grant_name_set:
            grant = self.grants['grants'][shortName]
            out += div % (grant['colour'], shortName)
        out += '</html>'
        return out

    def all_names(self):
        return list(self.grants['grants'].keys())

    def set_names(self, name_set):
        self.grant_name_set = name_set
        print('Restricting attention to ', self.grant_name_set)

##########
if __name__ == '__main__':
    import settings

    # read in the short names and other handmade bits
    gr = grants (settings.MYGRANTS)
    print('--------- Short names of grants')
    gr.print()

    # get the financials from the projects file
    gr.from_projects(settings.PROJECTS, settings.PROJECTS_DATE)

    # write out the full grants file
    gr.write(settings.DATA_DIR + '/grants.json')

    # see if it looks OK
    gr = grants(settings.DATA_DIR + '/grants.json')
    print('--------- Full data on grants')
    gr.print()

    # look at th colour chart
    out = gr.colour_chart()
    f = open('color.html', 'w')
    f.write(out)
    f.close()
