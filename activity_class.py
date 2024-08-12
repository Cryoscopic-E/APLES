from unified_planning.shortcuts import *
import custom_types as types
import fluents


class ActivityClass(InstantaneousAction):
    def __init__(self, name, score, activity_type):
        self.name = name
        self.score = score
        self.activity_type = activity_type

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

