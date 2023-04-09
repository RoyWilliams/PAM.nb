import sys, json

class people():
    def __init__(self, people_filename):
        data = json.loads(open(people_filename).read())
    
        # how much they cost as a multipe of their salary -- assumed constant
        self.cost_per_salary = data['cost_per_salary']
    
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

            people[person] = d
        self.people = people
        self.persons = people.keys()

    def print(self):
        print('Monthly cost per full-time person\nwith cost/salary ratio %6.3f\n' % self.cost_per_salary)
        print('Each line is: Name (spine) Cost')
        for person in self.persons:
            print('%12s (%7s) £%5.0f' % \
                (person, self.people[person]['spine'], self.people[person]['fulltimeCost']))

##########
if __name__ == '__main__':
    people = people('data/people.json')
    people.print()
