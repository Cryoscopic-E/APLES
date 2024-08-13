import csv

from unified_planning.shortcuts import *
import custom_types as types
import fluents


class ActivityClass(InstantaneousAction):
    def __init__(self, name, score, activity_type):
        self.name = name
        self.score = score
        self.activity_type = activity_type
        self.cost = 0

        if self.activity_type == 'physical':
            super().__init__(self.name, d=types.Difficulty, atype=types.Physical)
        elif self.activity_type == 'social':
            super().__init__(self.name, d=types.Difficulty, atype=types.Social)
        else:
            super().__init__(self.name, d=types.Difficulty, atype=types.General)

        # parameters
        d = self.parameter('d')
        atype = self.parameter('atype')
        # preconditions
        self.add_precondition(fluents.can_do_activity_type(atype))
        # effects
        if(self.activity_type == 'physical'):
            self.add_increase_effect(fluents.difficulty_lvl_physical(d), self.score)
        else:
            self.add_increase_effect(fluents.difficulty_lvl_social(d), self.score)



def gen_activity_from_data(data_path):
    # using csv file to generate activities
    activities = []
    with open(data_path, 'r') as f:
        reader = csv.reader(f)
        reader.__next__()
        for row in reader:
            # replace spaces with underscores
            row[0] = row[0].replace(' ', '_')
            # remove all non-alphanumeric characters except underscores
            row[0] = ''.join(e for e in row[0] if e.isalnum() or e == '_')
            # don't allow duplicate activities
            if row[0] in [a.name for a in activities]:
                continue

            activities.append(ActivityClass(row[0], int(row[1]), row[2]))
    return activities
