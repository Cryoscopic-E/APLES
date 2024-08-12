import csv

from unified_planning.shortcuts import *
import custom_types as types
import fluents


class ActivityClass(InstantaneousAction):
    def __init__(self, name, score):
        self.name = name
        self.score = score
        super().__init__(self.name, activity=types.Activity, d=types.Difficulty)
        # parameters
        act = self.parameter('activity')
        d = self.parameter('d')
        # preconditions
        self.add_precondition(fluents.can_do_activity(act))
        # effects
        self.add_increase_effect(fluents.difficulty_lvl(d), self.score)


def gen_activity_from_data(data_path):
    # using csv file to generate activities
    activities = []
    with open(data_path, 'r') as f:
        reader = csv.reader(f)
        reader.__next__()
        for row in reader:
            # replace spaces with underscores
            row[0] = row[0].replace(' ', '_')
            # remove all non-alphanumeric characters
            row[0] = ''.join(e for e in row[0] if e.isalnum())
            # don't allow duplicate activities
            if row[0] in [a.name for a in activities]:
                continue

            activities.append(ActivityClass(row[0], int(row[1])))
    return activities
