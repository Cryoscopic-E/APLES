from unified_planning.shortcuts import *

class RobotProblem:
    
    def __init__(self, initial_state: dict, robot_goals : dict):
        self.definition()
    
    def definition(self):
        self.problem = Problem('robot-assistant')

        # Types
        self.material_type = UserType('material')
        self.location_type = UserType('location')

        # Fluents
        self.at = Fluent('at', Bool, )
        

        #Actions
        self.move = InstantaneousAction('move')
        self.move.add_effect(self.at, True)
    

