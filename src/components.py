from unified_planning.model import UserType, Fluent, InstantaneousAction, Object

class Types:
    
    def __init__(self, types_path):
        self.types = {}
        self._init_types(types_path)
    
    def _init_types(self, types_path):
        activity_types = ['physical', 'general', 'social', 'cognitive', 'minigame']
        
        self._add_type('activity', UserType('activity'))
        
        for activity_type in activity_types:
            self.all_types[activity_type] = UserType(activity_type, self.all_types['activity'])

    def _add_type(self, name, type_obj):
        self.types[name] = type_obj
    
    @property
    def all_types(self):
        return self.types


class Fluents:

    def __init__(self, fluents_path, types):
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


