import csv
import os
import pandas as pd
from typing import Optional

sheet_data_path  = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'website', 'aples', 'data', 'sheet1.csv')
active_activity_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'website', 'aples', 'data', 'exampleactivities.csv')
graphs_data_path  = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Graph_experiment', 'graphs')

class Activity: 
    def __init__(self, name: str, _type: str, score: float, funscore: float):
        self.name = name
        self.type = _type
        self.score = score
        self.funscore = funscore

def get_graph_values(name = "none", index = 0):
    df_activities = pd.read_csv(active_activity_path)
    df = pd.read_csv(sheet_data_path)

    challenge_dict = df.groupby("challenge")["name"].apply(list).to_dict()
    challenge_status = {key: [0, 0, 0, 0, 0] for key in challenge_dict}

    for key, value in challenge_dict.items():
        activity_objects = []
        Physical = 0
        Social = 0
        Cognitive = 0
        Minigame = 0
        Funscore = 0

        for activity in value:
            activity_obj = get_activity_type_and_points(activity, df_activities)
            if activity_obj:
                activity_objects.append(activity_obj)

        for activity in activity_objects:
            if activity.type == "physical":
                Physical += activity.score
            elif activity.type == "social":
                Social += activity.score
            elif activity.type == "cognitive":
                Cognitive += activity.score
            elif activity.type == "minigame":
                Minigame += activity.score
            Funscore += activity.funscore

        # Avoid division by zero
        avg_funscore = Funscore / len(activity_objects) if activity_objects else 0

        challenge_status[key] = [Physical, Social, Cognitive, Minigame, avg_funscore]

    final_graph_values = []
    for key, value in challenge_status.items():
        final_graph_values.append(value)

    print_to_csv(final_graph_values, name, index)

def print_to_csv(values, name, index = 0):
    with open("real_{}_{}".format(name,index), mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["physical", "social", "cognitive", "funratio"])
        writer.writerows(values)
    
    print("written!!")


def get_activity_type_and_points(activity_name: str, df_activities: pd.DataFrame) -> Optional[Activity]:
    for _, activity in df_activities.iterrows(): 
        if activity_name == activity["Activities"]:
            return Activity(activity["Activities"], activity["Type"], activity["METScore"], activity["FunScore"])
    return None  # Explicitly return None when no match is found

def main():
    get_graph_values()

if __name__ == '__main__':
    main()
