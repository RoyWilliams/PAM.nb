import sys, json
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
    tok = monthTxt.split('-')
    if len(tok) == 3:   # day-month-year
        day = int(tok[0])
        month = monthNames.index(tok[1])
        year  = int(tok[2])
        if year > 2000: year -= 2000
        if day > 20:
            month += 1
        #print('3--', day, month, year)
    else:
        day = 1
        month = monthNames.index(tok[0])
        year  = int(tok[1])
        #print('2--', day, month, year)
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
        people_data = json.loads(open(people_filename).read())
        self.people = people_data['people']

    def findName(self, hint):
        line = hint.strip().lower()
        scoreDict = {}
        for name in self.people.keys():
            staffNumber = self.people[name]['staffNumber']
            if name.lower() in line or str(staffNumber) in line:
                scoreDict[name] = 1
            if 'otherNames' in self.people[name]:
                for otherName in self.people[name]['otherNames']:
                    if otherName.lower() in line:
                        if name in scoreDict.keys():
                            scoreDict[name] += 1
                        else:
                            scoreDict[name]  = 1
        maxName = None
        maxScore = 0
        for name,score in scoreDict.items():
            if score > maxScore:
                maxName = name
                maxScore = score

        if maxName:    return maxName 
        else:          return None


###### Changing P&M expense categories to WFAU categories
#    'Salary', 'Consumables', 'Travel', 'Equipment',
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
    return ['Salary', 'Travel', 'Equipment', 'Consumables']

def my_category(category):
    if category in category_ignore:
        return None
    if category in category_consumables:
        return 'Consumables'
    if category in category_salary:
        return 'Salary'
    if category in category_travel:
        return 'Travel'
    if category in category_equipment:
        return 'Equipment'

    print('ERROR Unknown expenditure category! "%s"' % category)
    return None

##########
if __name__ == '__main__':

    monthTxt = 'Dec-22'
    print(monthTxt)
    imonth = getMonthIndex(monthTxt)
    print(imonth)
    monthTxt = getMonthTxt(imonth)
    print(monthTxt)


    ns = nameSearcher('data/people.json')
    line = 'hello this is Rob Blake here'
    name = ns.findName(line)
    if name:
        print('%s --> %s' % (line.strip(), name))
    else:
        print('%s --> NOT FOUND' % line.strip())
