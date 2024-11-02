# plot files level_structure_x.csv
import os
#physical, social, cognitive
#0,0,0
#3,2,3

# plot social: 0 - 3
# plot physical: 0 - 2
# plot cognitive: 0 - 3



import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
def plot_level_structure(level_structure_path):
    levels = pd.read_csv(level_structure_path)
    fig, ax = plt.subplots(figsize=(10, 10))
    
    ax.plot(levels.index, levels['physical'], 'ro-', label='Physical')
    ax.plot(levels.index, levels['social'], 'bo-', label='Social')
    ax.plot(levels.index, levels['cognitive'], 'go-', label='Cognitive')
    
    ax.set_title('Levels')
    ax.set_xlabel('Days')  # Label for x-axis
    ax.set_ylabel('Difficulty')  # Label for y-axis
    ax.legend()
    ax.set_xlim(left=0)  # Ensure x-axis starts from 0
    ax.set_ylim(bottom=0)  # Ensure y-axis starts from 0
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))  # Enforce x-axis to use integer numbers
    
    plt.show()


# level_structure_path = os.path.join(os.path.dirname(__file__), 'data', 'level_structure_0.csv')
# plot_level_structure(level_structure_path)
# level_structure_path = os.path.join(os.path.dirname(__file__), 'data', 'level_structure_1.csv')
# plot_level_structure(level_structure_path)
# level_structure_path = os.path.join(os.path.dirname(__file__), 'data', 'level_structure_2.csv')
# plot_level_structure(level_structure_path)
# level_structure_path = os.path.join(os.path.dirname(__file__), 'data', 'level_structure_3.csv')
# plot_level_structure(level_structure_path)
# level_structure_path = os.path.join(os.path.dirname(__file__), 'data', 'level_structure_4.csv')
# plot_level_structure(level_structure_path)
# level_structure_path = os.path.join(os.path.dirname(__file__), 'data', 'level_structure_5.csv')
# plot_level_structure(level_structure_path)

import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

def plot_time_performance():
    p = os.path.join(os.path.dirname(__file__), 'time_performance.csv')
    time_performance = pd.read_csv(p)
    fig, ax = plt.subplots(figsize=(10, 10))
    
    ax.plot(time_performance['n_activities'], time_performance['time'], 'ro-')
    
    ax.set_title('Time performance')
    ax.set_xlabel('Number of activities')  # Label for x-axis
    ax.set_ylabel('Time (s)')  # Label for y-axis
    ax.set_xlim(left=0)  # Ensure x-axis starts from 0
    ax.set_ylim(bottom=0)  # Set y-axis from min to max value
    ax.set_xticks(time_performance['n_activities'])  # Set x-axis ticks to exact values of number of activities
    
    # Annotate each point with the number of levels
    for i, txt in enumerate(time_performance['n_levels']):
        ax.annotate(txt, (time_performance['n_activities'][i], time_performance['time'][i]), textcoords="offset points", xytext=(-10,-5), ha='center')
    
    # Custom legend for the number of levels
    custom_lines = [Line2D([0], [0], color='r', marker='o', linestyle='None', markersize=10, label='Number of Levels')]
    ax.legend(handles=custom_lines, loc='upper left')

    # Add grid lines on the y-axis
    ax.grid(axis='y')

    plt.show()

plot_time_performance()