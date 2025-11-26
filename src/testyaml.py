from yaml import safe_load

def main():
    # with open('./data/activities.yaml') as activities_cfg:
    #     activites = safe_load(activities_cfg)
    #     activities_types = list(activites.keys())
    #     print("Activity Types:", activities_types)
    #     for activity_type in activities_types:
    #         activity_list = activites[activity_type]
    #         print(f"Activities of type {activity_type}:")
    #         for activity in activity_list:
    #             for key, value in activity.items():
    #                 activity_name = key
    #                 met_score = value.get('MET_score', 0)
    #                 cost_increase = value.get('cost_increase', 0)
    #                 initial_cost = value.get('initial_cost', 0)
    #                 value = value.get('value', None)
    #                 print(f"  Name: {activity_name}, MET Score: {met_score}, Cost Increase: {cost_increase}, Initial Cost: {initial_cost}, Value: {value}")

    with open('./data/level_flow.yaml') as level_flow_cfg:
        level_flows = safe_load(level_flow_cfg)
        print("Level Flows:")
        activities_types = level_flows.keys()
        for activity_type in activities_types:
            flow_list = level_flows[activity_type]
            print(flow_list)

if __name__ == '__main__':
    main()