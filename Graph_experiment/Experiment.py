import csv
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy import stats
from scipy.stats import shapiro
from Experiment2 import get_graph_values

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'website', 'aples'))
from aples_manager import create_level_structure

graphs_data_path  = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Graph_experiment', 'graphs')
levels_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'website', 'aples', 'data', 'levelsExperiment.csv')

#TODO: If no plan is generated try to run the experiment with this activity file activated 
# active_activity_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'website', 'aples', 'data', 'exampleactivities.csv')
active_activity_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'website', 'aples', 'data', 'GeneratedActivities.csv')

activity_types = ['Physical', 'Social', 'Cognitive', 'Minigame']

flow1 = [ #FLOW
    [1, 2, 1, 0, 7],      # Level 1: Average = (1+2+1)/3 ≈ 1.33
    [2, 3, 1, 0, 7],      # Level 2: Average = (2+3+1)/3 = 2.00
    [2, 3, 3, 0, 7],      # Level 3: Average = (2+3+3)/3 ≈ 2.67
    [3, 5, 2, 0, 7],      # Level 4: Average = (3+5+2)/3 ≈ 3.33
    [4, 4, 6, 0, 6],      # Level 5: Average = (4+4+6)/3 ≈ 4.67
    [5, 6, 5, 0, 6],      # Level 6: Average = (5+6+5)/3 ≈ 5.33
    [6, 5, 7, 0, 5],      # Level 7: Average = (6+5+7)/3 = 6.00
    [7, 8, 6, 0, 5],      # Level 8: Average = (7+8+6)/3 = 7.00
    [7, 8, 8, 0, 5],      # Level 9: Average = (7+8+8)/3 ≈ 7.67
    [8, 9, 8, 0, 4],      # Level 10: Average = (8+9+8)/3 ≈ 8.33
    [9, 10, 9, 0,4]      # Level 11: Average = (9+10+9)/3 ≈ 9.33
]

flow2 = [
    [1, 2, 2, 0,   7],   # Level 1
    [3, 3, 4, 0,   7],   # Level 2
    [5, 5, 5, 0,   7],   # Level 3
    [6, 6, 6, 0,   7],   # Level 4
    [7, 7, 7, 0,   7],   # Level 5
    [8, 8, 9, 0,   7],   # Level 6
    [9, 10, 11, 0, 7], # Level 7
    [11, 11, 12, 0,6],# Level 8
    [12, 12, 14, 0,6],# Level 9
    [13, 13, 15, 0,6],# Level 10
    [14, 14, 17, 0,6],# Level 11
    [15, 16, 18, 0,6],# Level 12
    [17, 17, 19, 0,6],# Level 13
    [19, 19, 21, 0,6],# Level 14
    [20, 21, 22, 0,4],# Level 15
    [21, 23, 24, 0,4],# Level 16
    [22, 24, 26, 0,4],# Level 17
    [24, 26, 27, 0,4],# Level 18
    [25, 27, 28, 0,4],# Level 19
    [26, 28, 30, 0,4],# Level 20
    [27, 29, 31, 0,4] # Level 21
]



flow3 = [
    [1, 2, 2,    0,7],    
    [3, 3, 3,    0,7],    
    [5, 4, 4,    0,7],    
    [6, 5, 5,    0,7],    
    [8, 7, 7,    0,7],    
    [9, 8, 8,    0,7],    
    [11, 9, 9,   0,6],   
    [13, 10, 11, 0,6], 
    [15, 12, 12, 0,6], 
    [16, 13, 13, 0,6], 
    [17, 14, 14, 0,6], 
    [19, 15, 16, 0,6], 
    [20, 16, 17, 0,6], 
    [22, 18, 19, 0,6], 
    [24, 19, 21, 0,6], 
    [25, 20, 23, 0,6], 
    [27, 22, 25, 0,6], 
    [29, 24, 27, 0,5], 
    [31, 25, 29, 0,5], 
    [33, 26, 31, 0,5], 
    [34, 27, 33, 0,5], 
    [35, 28, 34, 0,5], 
    [36, 30, 35, 0,5], 
    [38, 31, 36, 0,5], 
    [39, 32, 38, 0,5], 
    [41, 33, 39, 0,5], 
    [43, 34, 40, 0,5], 
    [44, 36, 42, 0,5], 
    [46, 37, 43, 0,4], 
    [48, 39, 45, 0,4], 
    [50, 40, 47, 0,4]  
]

skill1 = [ #Skill Acquisition and Mastery Theory
    [1, 1, 1, 0,  7],   # Level 1:  (1+1+1)/3 ≈ 1.00  
    [2, 1, 2, 0,  7],   # Level 2:  (2+1+2)/3 ≈ 1.67  
    [4, 2, 3, 0,  7],   # Level 3:  (3+2+4)/3 ≈ 3.00  
    [6, 5, 4, 0,  7],   # Level 4:  (5+4+6)/3 ≈ 5.00  
    [6, 7, 8, 0,  6],   # Level 5:  (7+6+8)/3 ≈ 7.00  
    [9, 8, 9, 0,  6],   # Level 6:  (9+8+9)/3 ≈ 8.67  
    [10, 9, 10, 0,5], # Level 7:  (10+9+10)/3 ≈ 9.67  
    [10, 10, 9, 0,5], # Level 8:  (10+10+9)/3 ≈ 9.67  ← Plateau starts 
    [10, 9, 10, 0,5], # Level 9:  (10+9+10)/3 ≈ 9.67  
    [10, 10, 9, 0,4], # Level 10: (10+10+9)/3 ≈ 9.67  
    [9, 10, 10, 0,4], # Level 11: (9+10+10)/3 ≈ 9.67  ← Plateau continues 
]

skill2 = [ #Skill Acquisition and Mastery Theory
    [1, 1, 1, 0,   7],   # Level 1: (1+1+1)/3 ≈ 1.00  
    [2, 1, 2, 0,   7],   # Level 2: (2+1+2)/3 ≈ 1.67  
    [4, 2, 3, 0,   7],   # Level 3: (3+2+4)/3 ≈ 3.00  
    [6, 4, 5, 0,   7],   # Level 4: (6+4+5)/3 ≈ 5.00  
    [8, 6, 7, 0,   7],   # Level 5: (8+6+7)/3 ≈ 7.00  
    [10, 8, 9, 0,  7],  # Level 6: (10+8+9)/3 ≈ 9.00  
    [12, 10, 11, 0,7],# Level 7: (12+10+11)/3 ≈ 11.00  
    [13, 11, 12, 0,6],# Level 8: (13+11+12)/3 ≈ 12.00  
    [14, 12, 13, 0,6],# Level 9: (14+12+13)/3 ≈ 13.00  
    [15, 13, 14, 0,6],# Level 10: (15+13+14)/3 ≈ 14.00  
    [16, 14, 15, 0,6],# Level 11: (16+14+15)/3 ≈ 15.00  
    [17, 15, 16, 0,6],# Level 12: (17+15+16)/3 ≈ 16.00  
    [18, 16, 17, 0,6],# Level 13: (18+16+17)/3 ≈ 17.00  
    [19, 17, 18, 0,6],# Level 14: (19+17+18)/3 ≈ 18.00  
    [19, 18, 19, 0,4],# Level 15: (19+18+19)/3 ≈ 18.67  
    [19, 19, 19, 0,4],# Level 16: (19+19+19)/3 ≈ 19.00  
    [19, 19, 19, 0,4],# Level 17: (19+19+19)/3 ≈ 19.00  
    [19, 19, 19, 0,4],# Level 18: (19+19+19)/3 ≈ 19.00  
    [19, 19, 19, 0,4],# Level 19: (19+19+19)/3 ≈ 19.00  
    [19, 19, 19, 0,4],# Level 20: (19+19+19)/3 ≈ 19.00  
    [19, 19, 19, 0,4],# Level 21: (19+19+19)/3 ≈ 19.00
]

skill3 = [ #Skill Acquisition and Mastery Theory
    [1, 1, 1, 0,   7],    # Level 1:  (1+1+1)/3 ≈ 1.00  
    [2, 2, 2, 0,   7],    # Level 2:  (2+2+2)/3 ≈ 2.00  
    [3, 3, 3, 0,   7],    # Level 3:  (3+3+3)/3 ≈ 3.00  
    [5, 4, 5, 0,   7],    # Level 4:  (5+4+5)/3 ≈ 4.67  
    [7, 5, 6, 0,   7],    # Level 5:  (7+5+6)/3 ≈ 6.00  
    [9, 6, 7, 0,   7],    # Level 6:  (9+6+7)/3 ≈ 7.33  
    [11, 8, 9,0,   6],   # Level 7:  (11+8+9)/3 ≈ 9.33  
    [13, 9, 10, 0, 6],  # Level 8:  (13+9+10)/3 ≈ 10.67  
    [15, 10, 11, 0,6], # Level 9:  (15+10+11)/3 ≈ 12.00  
    [17, 11, 12, 0,6], # Level 10: (17+11+12)/3 ≈ 13.33  
    [19, 13, 14, 0,6], # Level 11: (19+13+14)/3 ≈ 15.33  
    [21, 14, 15, 0,6], # Level 12: (21+14+15)/3 ≈ 16.67  
    [22, 16, 17, 0,6], # Level 13: (22+16+17)/3 ≈ 18.33  
    [24, 17, 18, 0,6], # Level 14: (24+17+18)/3 ≈ 19.67  
    [25, 19, 20, 0,6], # Level 15: (25+19+20)/3 ≈ 21.33  
    [26, 20, 21, 0,6], # Level 16: (26+20+21)/3 ≈ 22.33  
    [27, 21, 22, 0,6], # Level 17: (27+21+22)/3 ≈ 23.33  
    [28, 22, 23, 0,5], # Level 18: (28+22+23)/3 ≈ 24.33  
    [29, 23, 24, 0,5], # Level 19: (29+23+24)/3 ≈ 25.33  
    [30, 24, 25, 0,5], # Level 20: (30+24+25)/3 ≈ 26.33  
    [30, 25, 26, 0,5], # Level 21: (30+25+26)/3 ≈ 27.00  
    [30, 25, 26, 0,5], # Level 22: (30+25+26)/3 ≈ 27.00  
    [30, 25, 26, 0,5], # Level 23: (30+25+26)/3 ≈ 27.00  
    [30, 25, 26, 0,5], # Level 24: (30+25+26)/3 ≈ 27.00  
    [30, 25, 26, 0,5], # Level 25: (30+25+26)/3 ≈ 27.00  
    [30, 25, 26, 0,5], # Level 26: (30+25+26)/3 ≈ 27.00  
    [30, 25, 26, 0,5], # Level 27: (30+25+26)/3 ≈ 27.00  
    [30, 25, 26, 0,5], # Level 28: (30+25+26)/3 ≈ 27.00  
    [30, 25, 26, 0,4], # Level 29: (30+25+26)/3 ≈ 27.00  
    [30, 25, 26, 0,4], # Level 30: (30+25+26)/3 ≈ 27.00  
    [30, 25, 26, 0,4], # Level 31: (30+25+26)/3 ≈ 27.00  
]




minigame1 = [  # With Minigames
    [0, 0, 1, 1, 7],   # Level 1:  (1+2+1)/3 ≈ 1.33  
    [0, 0, 1, 1, 7],   # Level 2:  (3+2+3)/3 ≈ 2.67  
    [0, 0, 1, 1, 7],   # Level 3:  (4+3+4)/3 ≈ 3.67  
    [1, 1, 0, 1, 7],   # Level 4:  (6+5+4)/3 ≈ 5.00  
    [1, 0, 2, 2, 6],   # Level 5:  (8+6+7)/3 ≈ 7.00  
    [2, 1, 2, 1, 6],   # Level 6:  (9+8+7)/3 ≈ 8.00  
    [3, 2, 1, 1, 5],   # Level 7:  (10+9+9)/3 ≈ 9.33  
    [4, 3, 1, 0, 5],   # Level 8:  (9+8+8)/3 ≈ 8.33  
    [5, 4, 2, 0, 5],   # Level 9:  (8+8+9)/3 ≈ 8.33  
    [6, 5, 2, 0, 4],   # Level 10: (7+7+7)/3 ≈ 7.00  
    [7, 6, 2, 0, 4],   # Level 11: (6+6+6)/3 ≈ 6.00  
]

minigame2 = [  # With Minigames and Cognitive Activities
    [1, 0, 0, 1, 7],   # Level 1:  (1+2+1)/3 ≈ 1.33  
    [0, 0, 1, 1, 7],   # Level 2:  (3+2+3)/3 ≈ 2.67  
    [0, 0, 2, 1, 7],   # Level 3:  (4+3+4)/3 ≈ 3.67  
    [1, 1, 1, 1, 7],   # Level 4:  (6+5+4)/3 ≈ 5.00  
    [1, 1, 2, 2, 7],   # Level 5:  (8+6+7)/3 ≈ 7.00  
    [2, 2, 2, 1, 7],  # Level 6:  (9+8+7)/3 ≈ 8.00  
    [3, 2, 2, 1, 7],   # Level 7:  (10+9+9)/3 ≈ 9.33  
    [3, 3, 2, 0, 6],   # Level 8:  (9+8+8)/3 ≈ 8.33  
    [4, 3, 3, 0, 6],   # Level 9:  (8+8+9)/3 ≈ 8.33  
    [5, 4, 3, 0, 6],   # Level 10: (7+7+7)/3 ≈ 7.00  
    [6, 5, 3, 0, 6],   # Level 11: (6+6+6)/3 ≈ 6.00  
    [6, 6, 2, 0, 6],   # Level 12: (5+5+6)/3 ≈ 5.33  
    [7, 6, 2, 0, 6],   # Level 13: (5+5+6)/3 ≈ 5.33  
    [8, 7, 2, 0, 6],   # Level 14: (4+4+5)/3 ≈ 4.33  
    [9, 7, 2, 0, 4],   # Level 15: (4+4+5)/3 ≈ 4.33  
    [10, 8, 2, 0,4],  # Level 16: (3+3+4)/3 ≈ 3.33  
    [10, 8, 1, 0,4],  # Level 17: (3+3+4)/3 ≈ 3.33  
    [10, 9, 1, 0,4],  # Level 18: (2+2+3)/3 ≈ 2.33  
    [10, 9, 1, 0,4],  # Level 19: (2+2+3)/3 ≈ 2.33  
    [10, 9, 1, 0,4],  # Level 20: (2+2+3)/3 ≈ 2.33  
    [10, 9, 1, 0,4]  # Level 21: (2+2+3)/3 ≈ 2.33  
]

minigame3 = [  # With Minigames and Cognitive Activities
    [1, 0, 0, 1, 7],   # Level 1:  (1+2+1)/3 ≈ 1.33  
    [0, 0, 1, 1, 7],   # Level 2:  (3+2+3)/3 ≈ 2.67  
    [0, 0, 2, 1, 7],   # Level 3:  (4+3+4)/3 ≈ 3.67  
    [1, 1, 1, 1, 7],   # Level 4:  (6+5+4)/3 ≈ 5.00  
    [1, 1, 2, 2, 7],   # Level 5:  (8+6+7)/3 ≈ 7.00  
    [2, 2, 2, 1, 7],   # Level 6:  (9+8+7)/3 ≈ 8.00  
    [3, 2, 2, 1, 6],   # Level 7:  (10+9+9)/3 ≈ 9.33  
    [3, 3, 2, 0, 6],   # Level 8:  (9+8+8)/3 ≈ 8.33  
    [4, 3, 3, 0, 6],   # Level 9:  (8+8+9)/3 ≈ 8.33  
    [5, 4, 3, 0, 6],   # Level 10: (7+7+7)/3 ≈ 7.00  
    [6, 5, 3, 0, 6],   # Level 11: (6+6+6)/3 ≈ 6.00  
    [6, 6, 2, 0, 6],   # Level 12: (5+5+6)/3 ≈ 5.33  
    [7, 6, 2, 0, 6],   # Level 13: (5+5+6)/3 ≈ 5.33  
    [8, 7, 2, 0, 6],   # Level 14: (4+4+5)/3 ≈ 4.33  
    [9, 7, 2, 0, 6],   # Level 15: (4+4+5)/3 ≈ 4.33  
    [10, 8, 2, 0,6],  # Level 16: (3+3+4)/3 ≈ 3.33  
    [10, 8, 1, 0,6],  # Level 17: (3+3+4)/3 ≈ 3.33  
    [8, 9, 1, 0, 5],  # Level 18: (2+2+3)/3 ≈ 2.33  
    [8, 10, 1, 0,5],  # Level 19: (2+2+3)/3 ≈ 2.33  
    [7, 8, 1, 0, 5],  # Level 20: (2+2+3)/3 ≈ 2.33  
    [9, 9, 1, 0, 5],  # Level 21: (2+2+3)/3 ≈ 2.33  
    [9, 9, 1, 0, 5],  # Level 22: (2+2+3)/3 ≈ 2.33  
    [9, 9, 0, 0, 5],  # Level 23: (1+2+3)/3 ≈ 2.00  
    [8, 10, 0, 0,5],  # Level 24: (1+2+3)/3 ≈ 2.00  
    [10, 9, 0, 0,5],  # Level 25: (1+2+3)/3 ≈ 2.00  
    [7, 9, 0, 0, 5],  # Level 26: (1+2+3)/3 ≈ 2.00  
    [8, 9, 0, 0, 5],  # Level 27: (1+2+3)/3 ≈ 2.00  
    [7, 9, 0, 0, 5],  # Level 28: (1+2+3)/3 ≈ 2.00  
    [6, 12, 0, 0,4],  # Level 29: (1+2+3)/3 ≈ 2.00  
    [8, 13, 0, 0,4],  # Level 30: (1+2+3)/3 ≈ 2.00  
    [10, 9, 0, 0,4]  # Level 31: (1+2+3)/3 ≈ 2.00  
]

flow_graph = [flow1, flow2, flow3]
skill_graph = [skill1,skill2,skill3]
minigame_graph = [minigame1,minigame2,minigame3]


def create_and_plot_graph(activity_types, difficulty_values, index, name, skip_newline=False):
    levels_new = []
    i = 0
    if skip_newline:
        df = pd.read_csv(difficulty_values, skiprows=1, header=None)  # Skip header
        difficulty_values = df.values.tolist()  # Convert DataFrame to a list of lists

    # Calculate the average difficulty for each level,
    # considering only Physical, Social, and Cognitive (ignoring Minigame)
    average_difficulties = []
    for row in difficulty_values:
        levels_new.append(i)
        # Only consider the first three values
        non_zero = [d for d in row[:3] if float(d) > 0]
        avg = np.mean(non_zero) if non_zero else 0
        average_difficulties.append(avg)
        i = i + 1

    
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot each activity type's difficulty progression
    for j, activity in enumerate(activity_types):
        ax.plot(levels_new, [row[j] for row in difficulty_values],
                label=activity, marker='o')

    # Plot the average difficulty line (the flow line) as a dashed black line
    ax.plot(levels_new, average_difficulties, label='Average Difficulty', 
            color='black', linestyle='--', marker='x')

    # Adding labels and title
    ax.set_xlabel('Levels')
    ax.set_ylabel('Difficulty')
    ax.set_title('Activity Difficulty by Level')

    # Adding a legend
    ax.legend(title='Activity Types')
    plt.tight_layout()
    plt.savefig('{}/{}graph{}.png'.format(graphs_data_path, name, index))
    # plt.show()

    return average_difficulties

def create_level_csv(graph):
    print_to_csv(graph)

def print_to_csv(values):
    with open(levels_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["physical", "social", "cognitive","minigame", "funratio"])
        writer.writerows(values)
    print("written!!")

def clean_real_graph_data(path):
    df = pd.read_csv(path, skiprows=1, header=None)  # Skip header
    difficulty_values = df.values.tolist()  # Convert DataFrame to a list of lists
    return difficulty_values

def create_real_vs_input_fun_graph(array1,array2, index, name, context):
    
    if context == "fun":
        array2 = clean_real_graph_data(array2)
        array1 = get_fun_ratio_from_array(array1)
        array2 = get_fun_ratio_from_array(array2)

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot array 1 and array 2 
    ax.plot(array1, label="Input {}".format(context), marker="o", linestyle="-", color="b")
    ax.plot(array2, label="Real {}".format(context), marker="s", linestyle="--", color="r")

    # Adding labels and title
    ax.set_xlabel('Levels')
    ax.set_ylabel('{} level'.format(context))
    ax.set_title('Average {} comparison graph'.format(context))

    # Adding a legend
    ax.legend(title='Activity Types')
    plt.tight_layout()
    plt.savefig('{}/{}-{}-comparison-graph-{}.png'.format(graphs_data_path,name, context , index))

    return [array1,array2]

def get_fun_ratio_from_array(array):
    funratio = []
    for item in array:
        funratio.append(item[4])
    return funratio

def statistical_analysis(array1, array2, text_file, name, input):
        text_file.write("----------------- \n")
        text_file.write("Content: {} - {} \n".format(name, input))        
        array1_normality = shapiro(array1).pvalue
        text_file.write("Test of Normality array 1: {} \n".format(array1_normality))
        array2_normality = shapiro(array2).pvalue
        text_file.write("Test of Normality array 2: {} \n".format(array2_normality))

        if array1_normality <= 0.05 and array2_normality <= 0.05:
            text_file.write("Normal contribution is true \n")
            text_file.write("Test significant difference between groups using independent t-tests: ")
            result = stats.ttest_ind(a=array1, b=array2, equal_var=True).pvalue
            text_file.write("P-value = {} \n".format(result))
            if result > 0.05:
                text_file.write("There is no significant difference between the two graphs using t-test \n")
            else:
                text_file.write("There is significant difference between the two graphs using t-tests \n")
        else:
            text_file.write("Normal contribution is False \n")
            text_file.write("Test significant difference between groups using kruskal-wallis test: ")
            result = stats.kruskal(array1,array2).pvalue
            text_file.write("P-value = {} \n".format(result))
            if result > 0.05:
                text_file.write("There is no significant difference between the two graphs using kw test \n")
            else:
                text_file.write("There is significant difference between the two graphs using kw test \n")
        text_file.write("----------------- \n")
def save_graph(graphs, name, text_file):
    index = 0
    text_file.write("\n {} \n".format(name))
    for graph in graphs:
        #plot and save the graph
        avg_input_difficulty = create_and_plot_graph(activity_types, graph, index, name)
        #Add the plotted graph to the current level
        create_level_csv(graph)
        #Create a plan using the planner
        create_level_structure(levels_path,active_activity_path)
        #plot* and save the "planned" graphs
        get_graph_values(name, index)
        avg_real_difficulty = create_and_plot_graph(activity_types,"{}/real_{}_{}.csv".format(graphs_data_path,name,index),index, "actual_{}graph{}".format(name, index), True)
        average_fun_arrays = create_real_vs_input_fun_graph(graph,"{}/real_{}_{}.csv".format(graphs_data_path,name,index), index, name, "fun")
        average_difficulty_arrays = create_real_vs_input_fun_graph(avg_input_difficulty,avg_real_difficulty, index, name, "difficulty")
        statistical_analysis(average_fun_arrays[0], average_fun_arrays[1], text_file, name + " fun ", index)
        statistical_analysis(avg_input_difficulty, avg_real_difficulty, text_file, name + " difficulty ", index)
        index = index + 1

def main():
    with open("{}/output.txt".format(graphs_data_path), "w") as text_file:
        save_graph(flow_graph, "flow", text_file)
        save_graph(skill_graph, "skill", text_file)
        save_graph(minigame_graph, "minigame", text_file)

if __name__ == '__main__':
    main()
