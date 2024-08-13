from unified_planning.shortcuts import *

Activity = UserType('Activity')
Difficulty = UserType('Difficulty')
Physical = UserType('Physical', Activity)
General = UserType('General', Activity)
Social = UserType('Social', Activity)
Cognitive = UserType('Cognitive', Activity)