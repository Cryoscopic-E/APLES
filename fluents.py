from unified_planning.shortcuts import *
import custom_types as types
from unified_planning.model.types import BOOL

difficulty_lvl = Fluent('difficulty_lvl', IntType(), d=types.Difficulty)
difficulty_lvl_social = Fluent('difficulty_lvl_social', IntType(), d=types.Difficulty)
difficulty_lvl_physical = Fluent('difficulty_lvl_physical', IntType(), d=types.Difficulty)

can_do_activity_type = Fluent('CanDoActivityType', BOOL, activityType=types.Activity)