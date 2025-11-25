from unified_planning.model import UserType, Fluent, InstantaneousAction, Object
from enum import Enum, auto

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

class Fluents:

    def __init__(self, fluents : set, types : set):
        self.types = types
        self.fluents = {}
        self._init_fluents(fluents_path)
    
    def _init_fluents(self, fluents_path):
        """
        Initialises fluents from a yaml file
        Args:
            fluents_path (_type_): _description_
        """
        with open(fluents_path, 'r') as f:
            fluents_data = yaml.safe_load(f)
            for fluent_name, fluent_info in fluents_data.items():
                fluent_type = self.types[fluent_info['type']]
                fluent = Fluent(fluent_name, fluent_type)
                self._add_fluent(fluent_name, fluent)

    def _add_fluent(self, name, fluent):
        self.fluents[name] = fluent
    
    @property
    def all_fluents(self):
        return self.fluents

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
        self.add_precondition(fluents['can_do_activity_type'](atype))
        # current cost effect
        self.add_increase_effect(fluents['cost_' + self.name], self.cost_increase)
        

