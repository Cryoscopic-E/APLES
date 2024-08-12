from unified_planning.shortcuts import *
import custom_types as types
import fluents


class ActivityClass(InstantaneousAction):
    def __init__(self, name, score, activity_type):
        self.name = name
        self.score = score
        self.activity_type = activity_type
        super().__init__(self.name, activity=types.Activity, d=types.Difficulty)
        # parameters
        act = self.parameter('activity')
        d = self.parameter('d')
        # preconditions
        self.add_precondition(fluents.can_do_activity(act))
        # effects
        if(self.activity_type == 'physical'):
            self.add_increase_effect(fluents.difficulty_lvl_physical(d), self.score)
        else:
            self.add_increase_effect(fluents.difficulty_lvl_social(d), self.score)

