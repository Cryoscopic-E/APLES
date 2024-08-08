from unified_planning.shortcuts import *
import custom_types as types
from unified_planning.model.types import BOOL

difficulty_lvl = Fluent('difficulty_lvl', IntType(), d=types.Difficulty)
can_do_activity = Fluent('CanDoActivity', BOOL, activity=types.Activity)