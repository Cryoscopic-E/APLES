from unified_planning.engines import PlanGenerationResult

class PlanManager:
    def __init__(self, activities_plan : PlanGenerationResult):
        self.activities_plan = activities_plan
    