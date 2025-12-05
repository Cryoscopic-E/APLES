from unified_planning.model import Fluent, InstantaneousAction, Object
from unified_planning.shortcuts import LE, Real, Int, Equals, Not
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
    def __init__(self, name, score, cost_increase, activity_type : ActivityType, fluents, types, type_id, max_repetitions=None, requires_tutorial=False):
        super().__init__(name, atype=types[activity_mappings[activity_type][0]])
        self.original_name = name
        self.score = score
        self.activity_type = activity_type
        self.cost_increase = cost_increase

        if self.activity_type in activity_mappings:
            atype, fluent = activity_mappings[self.activity_type]
            self.add_increase_effect(fluents[fluent], self.score)
        else:
            raise ValueError('Activity type not recognized when creating action effects')

        # parameters
        # atype = self.parameter('atype') # This seems unused or redundant if not careful, but keeping super init clean.
        # Note: In the original code `super().__init__(action_name, atype=types[atype])` used `types[atype]`.
        # Here I moved super call up.
        
        self.add_precondition(fluents['can_do_' + self.original_name])
        
        # Max repetitions logic
        if max_repetitions is not None:
            count_fluent = fluents['count_' + self.original_name]
            self.add_precondition(LE(count_fluent, max_repetitions - 1))
            self.add_increase_effect(count_fluent, 1)
        
        # current cost effect (always update the base cost fluent)
        self.add_increase_effect(fluents['cost_' + self.original_name], self.cost_increase)


        

