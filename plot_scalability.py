import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import sys
from datetime import datetime

# Define a function to redirect stdout to a file
def redirect_stdout_to_file(filepath):
    class Tee:
        def __init__(self, *files):
            self.files = files
        def write(self, obj):
            for f in self.files:
                f.write(obj)
        def flush(self):
            for f in self.files:
                f.flush()

    log_file = open(filepath, 'a') # Open in append mode
    original_stdout = sys.stdout
    sys.stdout = Tee(original_stdout, log_file)
    return log_file, original_stdout

# Start of script logic
# Load the data
csv_file = 'experiment_scalability_results.csv'
if not os.path.exists(csv_file):
    print(f"Error: {csv_file} not found.")
    sys.exit(1)

df = pd.read_csv(csv_file)

# Ensure output directory exists
output_dir = 'results'
os.makedirs(output_dir, exist_ok=True)

# Define the log file path
log_filepath = os.path.join(output_dir, 'plotting_log.txt')

# Redirect stdout to the log file
log_file, original_stdout = redirect_stdout_to_file(log_filepath)

try:
    print(f"--- Plotting and Analysis Log ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
    print(f"Loading data from: {csv_file}")

    # Set style
    sns.set(style="whitegrid", context="paper", font_scale=1.2)

    # 1. Planning Time vs Difficulty Level (Grouped by Category)
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=df, x='level', y='generation_time', hue='category', style='category', markers=True, dashes=False, linewidth=2.5)
    plt.title('Planning Time vs Difficulty Level', fontsize=16)
    plt.xlabel('Difficulty Level', fontsize=14)
    plt.ylabel('Generation Time (s)', fontsize=14)
    plt.legend(title='Category', title_fontsize='13', fontsize='12')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'time_vs_level_by_category.png'))
    plt.close()
    print(f"Plot saved: {os.path.join(output_dir, 'time_vs_level_by_category.png')}")

    # 2. Plan Length vs Difficulty Level (Grouped by Category)
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=df, x='level', y='plan_length', hue='category', style='category', markers=True, dashes=False, linewidth=2.5)
    plt.title('Plan Length vs Difficulty Level', fontsize=16)
    plt.xlabel('Difficulty Level', fontsize=14)
    plt.ylabel('Plan Length (Actions)', fontsize=14)
    plt.legend(title='Category', title_fontsize='13', fontsize='12')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'length_vs_level_by_category.png'))
    plt.close()
    print(f"Plot saved: {os.path.join(output_dir, 'length_vs_level_by_category.png')}")

    # 3. Planning Time Distribution by Category (Boxplot)
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='category', y='generation_time', palette="Set2")
    plt.title('Distribution of Planning Time by Category', fontsize=16)
    plt.xlabel('Category', fontsize=14)
    plt.ylabel('Generation Time (s)', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'time_distribution_boxplot.png'))
    plt.close()
    print(f"Plot saved: {os.path.join(output_dir, 'time_distribution_boxplot.png')}")

    # 4. Plan Cost vs Level (NEW)
    if 'plan_cost' in df.columns:
        plt.figure(figsize=(12, 7))
        sns.lineplot(data=df, x='level', y='plan_cost', hue='category', style='category', markers=True, dashes=False, linewidth=2.5)
        plt.title('Plan Cost vs Difficulty Level', fontsize=16)
        plt.xlabel('Difficulty Level', fontsize=14)
        plt.ylabel('Total Plan Cost', fontsize=14)
        plt.legend(title='Category', title_fontsize='13', fontsize='12')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'cost_vs_level_by_category.png'))
        plt.close()
        print(f"Plot saved: {os.path.join(output_dir, 'cost_vs_level_by_category.png')}")

    # Helper for stats
    def is_success(status):
        return "SOLVED" in str(status)

    df['success'] = df['status'].apply(is_success)

    print(f"All plots saved to {output_dir}/ directory.")

    # --- Statistical Analysis Report ---
    print("\n=== Extended Statistical Analysis ===")
    categories = df['category'].unique()

    for cat in categories:
        cat_df = df[df['category'] == cat]
        
        # Filter only successful runs for time/length stats
        success_df = cat_df[cat_df['success']]
        
        print(f"\nCategory: {cat.capitalize()}")
        print(f"  Total Runs: {len(cat_df)}")
        print(f"  Successful Runs: {len(success_df)} ({len(success_df)/len(cat_df)*100:.1f}%)")
        
        if not success_df.empty:
            avg_time = success_df['generation_time'].mean()
            avg_len = success_df['plan_length'].mean()
            avg_cost = success_df['plan_cost'].mean() if 'plan_cost' in success_df.columns else 0
            
            print(f"  Avg Generation Time: {avg_time:.4f} s")
            print(f"  Avg Plan Length: {avg_len:.2f} actions")
            print(f"  Avg Plan Cost: {avg_cost:.2f}")
            
            # Correlation
            if len(success_df) > 1:
                corr_time = np.corrcoef(success_df['level'], success_df['generation_time'])[0, 1]
                corr_len = np.corrcoef(success_df['level'], success_df['plan_length'])[0, 1]
                print(f"  Correlation (Level vs Time): {corr_time:.4f}")
                print(f"  Correlation (Level vs Length): {corr_len:.4f}")
                
                if 'plan_cost' in success_df.columns:
                    corr_cost = np.corrcoef(success_df['level'], success_df['plan_cost'])[0, 1]
                    print(f"  Correlation (Level vs Cost): {corr_cost:.4f}")
    else:
        print("  No successful runs to analyze.")

finally:
    # Restore original stdout and close the log file
    sys.stdout = original_stdout
    log_file.close()
    print(f"Plotting log saved to {log_filepath}")