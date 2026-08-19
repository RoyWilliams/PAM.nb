import sys, json, re
import settings
monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

###### Converting text month (eg Jul-23) back and forth to number
def getMonthTxt(monthIndex):
    year = monthIndex // 12
    month = monthNames[monthIndex % 12]
    return month +'-'+ '%02d'%year

def dateTimeToMonthTxt(dt):
    # python datetime to string 31-Mar-2024
    dt = str(dt)
    #print('====', dt)
    tok = dt.split()
    if len(tok) == 2:
        tok = tok[0].split('-')
        year  = tok[0]
        month = monthNames[int(tok[1])-1]
        day   = tok[2]
        #print('2--', year, month, day)
    else:
        tok = dt.split('/')
        day   = tok[0]
        month = monthNames[int(tok[1])-1]
        year  = tok[2][-2:]   # reduces 2022 to 22
        #print('1--', year, month, day)
    monthTxt = '%02s-%03s-%4s' % (day, month, year)
    return monthTxt

def getMonthIndex(monthTxt):
    monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthTxt = str(monthTxt)
#    print(monthTxt, end = ':')
    tokd  = monthTxt.split('-')
    toks  = monthTxt.split('/')
    tokc = monthTxt.split(':')

    if len(tokc) > 1:         # excel date-time 2022-07-28 00:00:00:
        tokd  = monthTxt.split(' ')[0].split('-')
        year  = int(tokd[0])
        month = int(tokd[1])
        day   = int(tokd[2])
        if year > 2000: year -= 2000
#        print('y-m-d', year, month, day)

    elif len(tokd) == 3:   # string 2022-07-28
        day = int(tokd[0])
        month = monthNames.index(tokd[1])
        year  = int(tokd[2])
        if year > 2000: year -= 2000
#        print('d-m-y', day, month, year)

    elif len(tokd) == 2:   # string Jan-22
        day = 1
        month = monthNames.index(tokd[0]) + 1
        year  = int(tokd[1])
#        print('m-y', day, month, year)

    elif len(toks) == 3:   # string 28/09/2022
        day = int(toks[0])
        month = int(toks[1]) + 1
        year  = int(toks[2]) - 2000
        print('d/m/y', day, month, year)

    else:
        print(f'Cannot read data from {monthTxt}')
        return None
            
    return year*12 + month  # month number with Jan 2000 = 1

###### The start and end of the run
class run():
    def __init__(self, start_month, end_month):
        self.istart = getMonthIndex(start_month)
        self.iend   = getMonthIndex(end_month)
        self.nmonth = self.iend - self.istart

    def print(self):
        start = getMonthTxt(self.istart)
        end   = getMonthTxt(self.iend)
        print('Run is from %s to %s (%d months)' % (start, end, self.nmonth))

###### Searching for names in crap
class nameSearcher():
    def __init__(self, people_filename):
        self.people = {}
        data = json.loads(open(people_filename).read())
        for costChange in data:
            person      = costChange[0]
            staffNumber = costChange[1]
            self.people[person] = { 'staffNumber': staffNumber }

    def findName(self, row):
# Given a row from the transactions file, we need to know if its a "human cost"
# meaning salary + overheads
# and if so the last name of who is getting the salary
        originator = str(row['Originator'])
        comments = str(row['Comments'])
        otr = str(row['Original Transaction Reference'])
        staffNumber = 0

        if originator == 'nan':
            return None

        originator_tok = originator.split(',')
        last_name = originator_tok[0].strip()
        first_name = originator_tok[1].strip()

        if otr.startswith('426_'):
            matches = re.findall(r'E\d+', otr)
            if len(matches) > 0:
                staffNumber = int(matches[0][1:])

        if comments.find(last_name) >= 0:
            matches = re.findall(r'\d{4,}', comments)
            if len(matches) > 0:
                staffNumber = int(matches[0])

        person = last_name
        if self.people[person]['staffNumber'] == staffNumber:
            return person
        else:
            return None

###### Changing P&M expense categories to WFAU categories
#    'Human Cost', 'Consumables', 'Travel', 'Equipment',
# and ignoring those we arent interested in

category_ignore = [
    'nan',
    'Total Award',
    'Grant Income',
    'Financial Resources',
    'Directly Allocated - Co-Principal Investigator Staff',
    'Directly Allocated - Estates Costs',
    'Directly Allocated - Infrastructure Technician Costs',
    'Directly Allocated - Principal Investigator Staff',
    'Directly Allocated - Co-Principal Investigator Staff',
    'Directly Allocated Research Administration Staff',
    'Indirect Costs',
]
category_consumables = [
    'Consumables - Research Other Costs',
    'Consumables - IT',
    'Consumables - Telephone and Communication',
    'Consumables - Printing Postage and Stationery',
    'Consumables - Research Consumables',
    'Staff Conf Course and Seminar Fees',
    'Other Directly Incurred',
]

category_salary = [
    'Research Investigator',
    'Research Assistant'
]

category_travel    = ['Travel and Subsistence']
category_equipment = ['Equipment']

def categories():
    return ['Human Cost', 'Travel', 'Equipment', 'Consumables']

def my_category(category):
    if category in category_ignore:
        return None
    if category in category_consumables:
        return 'Consumables'
    if category in category_salary:
        return 'Human Cost'
    if category in category_travel:
        return 'Travel'
    if category in category_equipment:
        return 'Equipment'

    print('ERROR Unknown expenditure category! "%s"' % category)
    return None

def print_settings():
    print('mygrantsjson is            ', settings.MYGRANTS, ' dated ', settings.GRANTS_DATE)
    print('projects spreadsheet is    ', settings.PROJECTS)
    print('people.json is             ', settings.PEOPLE)
    print('assign.json is             ', settings.ASSIGN)
    print('transactions spreadsheet is', settings.TRANSACTIONS)
    print('This run is from', settings.RUN_START, 'to', settings.RUN_END)
