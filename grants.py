import sys, json
import pandas as pd
import util

# Reads in a list of grants and their shortnames
# Can also read in financial information from the projects.xls file

class grants():
    def __init__(self, grants_filename):
        self.grants_filename = grants_filename
        self.grants = json.loads(open(grants_filename, 'r').read())
        mygr = self.grants['grants']
        self.mygrant_names = mygr.keys()
        self.ends = {}
        if 'month' in self.grants:
            self.month = self.grants['month']
        for grantName, data in mygr.items():
            if 'end' in data:
                self.ends[grantName] = data['end']

    def from_projects(self, project_filename, month):
        mygr = self.grants['grants']
        projectId_to_shortName = {}
        for k,v in mygr.items():
            projectId_to_shortName[v['projectId']] = k

        # Now read the P&M file
        pam = pd.read_excel(project_filename)
    
        old_grant = ''
        for index, row in pam.iterrows():
            project = row['Project Number']
            if project not in projectId_to_shortName:
                print('ERROR PaM projectID not in mygrants.json: %s - %s' % (project, row['Project Name']))
                continue

            shortName = projectId_to_shortName[project]
            grant = mygr[shortName]
        
            if grant != old_grant:
                grant['projectId'] = project
                grant['start'] = row['Start Date']
                grant['end']   = row['End Date']
                grant['awarded']   = {}
                grant['spent'] = {}
                for category in util.categories():
                    grant['awarded'][category] = 0
                    grant['spent'][category]   = 0
                # if end date specified in mygrants.json, use that
                if shortName in list(self.ends.keys()):
                    grant['end']   = self.ends[shortName]
                    print("%s end date set to %s from %s" % \
                        (shortName, grant['end'], self.grants_filename))
    
            their_category = str(row['Account'])
            category = util.my_category(their_category)
            if not category:
                continue
            awarded = float(row['Budget'])
            grant['awarded'][category] += awarded

            spent   = float(row['Actual to Date'])
            grant['spent']  [category] += spent

            old_grant = grant

        # check that each mygrant was in the PAM report
        for shortName, grant in self.grants['grants'].items():
            if not 'awarded' in grant:
                print('WARNING: %s in mygrants not found in PAM file' % shortName)

        self.grants = {'month':month, 'grants':mygr}
        self.grant_names = mygr.keys()

    def print(self):
        if 'month' in self.grants:
            print('As of beginning of %s' % self.grants['month'])
        for shortName, grant in self.grants['grants'].items():
            print(shortName)
            print('  ', grant['fullName'])
            print('  P&M project ', grant['projectId'])
            
            if 'start' in grant:
                nmonth = util.getMonthIndex(grant['end']) - util.getMonthIndex(grant['start'])
                print('   Start %s, End %s (%d months)' % (grant['start'], grant['end'], nmonth))
            if 'awarded' in grant:
                print('   Awarded     Spent    Category')
                for category in grant['awarded']:
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
        for shortName, grant in self.grants['grants'].items():
            out += div % (grant['colour'], shortName)
        out += '</html>'
        return out

##########
if __name__ == '__main__':
    # read in the short names and other handmade bits
    g = grants('data/grants.json')
    print('--------- Short names of grants')
    g.print()

    # get the financials from the projects file
    g.from_projects('data/project_Aug-22.xls', 'Aug-22')
    # write out the full grants file
    g.write('data/grants.json')
    # see if it looks OK
    g = grants('data/grants.json')
    print('--------- Full data on grants')
    g.print()

    out = g.colour_chart()
    f = open('color.html', 'w')
    f.write(out)
    f.close()
