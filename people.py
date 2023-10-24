import sys, json

class people():
    def __init__(self, people_filename):
        try:
            data = json.loads(open(people_filename).read())
        except Exception as e:
            print('Error with people file: %s' % str(e))
    

        # how much they cost as a multipe of their salary -- assumed constant
        self.cost_per_salary = data['cost_per_salary']

        self.staffNumber_to_person = {}
    
        people = {}
        dp = data['people']
        for person in dp.keys():
            d = {}
            if 'salary' in dp[person]:
                d['fulltimeCost'] = dp[person]['salary'] * self.cost_per_salary / 12
            else:
                print('ERROR: %s has no fulltimeCost (salary)' % person)
                continue
            if 'spine' in dp[person]:
                d['spine'] = dp[person]['spine']
            if 'staffNumber' in dp[person]:
                d['staffNumber'] = dp[person]['staffNumber']
                self.staffNumber_to_person[dp[person]['staffNumber']] = person

            people[person] = d
        self.people = people
        self.people_name_set = people.keys()

    def print(self):
        print('Monthly cost per full-time person\nwith cost/salary ratio %6.3f\n' % self.cost_per_salary)
        print('Each line is: Name (spine) Cost')
        for person in self.people_name_set:
            print('%12s (%7s) £%5.0f' % \
                (person, self.people[person]['spine'], self.people[person]['fulltimeCost']))

    def all_names(self):
        return list(self.people.keys())

    def set_names(self, person_set):
        self.people_name_set = person_set
        print('Restricting attention to ', self.people_name_set)

    def get_person(self, staffNumber):
        if staffNumber in self.staffNumber_to_person:
            return self.staffNumber_to_person[staffNumber]
        else:
            print('ERROR: staff number %d not in people file' % staffNumber)
            return None

##########
if __name__ == '__main__':
    import settings
    pe = people(settings.PEOPLE)
    pe.print()
