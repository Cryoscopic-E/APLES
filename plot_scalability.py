import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load the data
csv_file = 'experiment_scalability_results.csv'
if not os.path.exists(csv_file):
    print(f"Error: {csv_file} not found.")
    exit(1)

df = pd.read_csv(csv_file)

# Set style
sns.set(style="whitegrid")

# Plot 1: Generation Time vs Domain Size (Hue: Level)
plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='domain_size', y='generation_time', hue='level', marker='o', palette='viridis')
plt.title('Planning Time vs Domain Size (Grouped by Difficulty Level)')
plt.xlabel('Number of Activities per Category (Domain Size)')
plt.ylabel('Generation Time (s)')
plt.legend(title='Difficulty Level')
plt.savefig('scalability_time_vs_domain.png')
plt.close()

# Plot 2: Generation Time vs Level (Hue: Domain Size)
plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='level', y='generation_time', hue='domain_size', marker='o', palette='rocket')
plt.title('Planning Time vs Difficulty Level (Grouped by Domain Size)')
plt.xlabel('Difficulty Level')
plt.ylabel('Generation Time (s)')
plt.legend(title='Domain Size')
plt.savefig('scalability_time_vs_level.png')
plt.close()

# Plot 3: Plan Length vs Level (Hue: Domain Size)
plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='level', y='plan_length', hue='domain_size', marker='o', palette='mako')
plt.title('Plan Length vs Difficulty Level')
plt.xlabel('Difficulty Level')
plt.ylabel('Plan Length (Actions)')
plt.legend(title='Domain Size')
plt.savefig('scalability_plan_length.png')
plt.close()

print("Plots saved: scalability_time_vs_domain.png, scalability_time_vs_level.png, scalability_plan_length.png")
