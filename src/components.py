from unified_planning.model import Fluent, InstantaneousAction, Object
from unified_planning.shortcuts import LE, Real, Int
from enum import Enum, auto
import yaml

class ActivityType(Enum):
    PHYSICAL = auto()
    SOCIAL = auto()
    COGNITIVE = auto()
    GENERAL = auto()


activity_mappings = {
    ActivityType.PHYSICAL: ('physical', 'difficulty_lvl_physical'),
    ActivityType.SOCIAL: ('social', 'difficulty_lvl_social'),
    ActivityType.COGNITIVE: ('cognitive', 'difficulty_lvl_cognitive'),
    ActivityType.GENERAL: ('general', 'difficulty_lvl'),
}

activity_type_mapping = {
    'physical': ActivityType.PHYSICAL,
    'social': ActivityType.SOCIAL,
    'cognitive': ActivityType.COGNITIVE,
    'general': ActivityType.GENERAL,
}

class ActivityAction(InstantaneousAction):
    def __init__(self, name, score, cost_increase, activity_type : ActivityType, fluents, types):
        self.name = name
        self.score = score
        self.activity_type = activity_type
        self.cost_increase = cost_increase

        if self.activity_type in activity_mappings:
            atype, fluent = activity_mappings[self.activity_type]
            super().__init__(self.name, atype=types[atype])
            self.add_increase_effect(fluents[fluent], self.score)
        else:
            raise ValueError('Activity type not recognized when creating action effects')

        # parameters
        atype = self.parameter('atype')
        # preconditions
        #self.add_precondition(fluents['can_do_activity_type'](atype) &  LE(fluents['cost_' + self.name], fluents[fluent]))
        self.add_precondition(fluents['can_do_activity_type'](atype))
        # current cost effect
        self.add_increase_effect(fluents['cost_' + self.name], self.cost_increase)
        

