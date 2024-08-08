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
