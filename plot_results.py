import pandas as pd
import matplotlib.pyplot as plt
import os

# Load the data
csv_file = 'experiment_results.csv'
if not os.path.exists(csv_file):
    print(f"Error: {csv_file} not found.")
    exit(1)

df = pd.read_csv(csv_file)

# Plot 1: Plan Length vs Level
plt.figure(figsize=(10, 6))
plt.plot(df['level'], df['plan_length'], marker='o', linestyle='-', color='b')
plt.title('Plan Length vs Level')
plt.xlabel('Level')
plt.ylabel('Plan Length (Number of Actions)')
plt.grid(True)
plt.savefig('plan_length_vs_level.png')
plt.close()

# Plot 2: Generation Time vs Level
plt.figure(figsize=(10, 6))
plt.plot(df['level'], df['generation_time'], marker='x', linestyle='-', color='r')
plt.title('Generation Time vs Level')
plt.xlabel('Level')
plt.ylabel('Generation Time (seconds)')
plt.grid(True)
plt.savefig('generation_time_vs_level.png')
plt.close()

print("Plots saved as 'plan_length_vs_level.png' and 'generation_time_vs_level.png'")
