import json
import yaml
import math
import re
from collections import Counter

def calculate_entropy(counts):
    total = sum(counts.values())
    if total == 0:
        return 0.0
    probabilities = [count / total for count in counts.values()]
    entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
    return entropy

def parse_activity_plan(plan_str):
    activities = []
    if not plan_str:
        return activities
    
    lines = plan_str.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith("SequentialPlan"):
            continue
        if not line:
            continue
        
        # Match pattern like "Walk_10k(physical_activity)" -> "Walk_10k"
        match = re.match(r'^(\w+)\(', line)
        if match:
            activities.append(match.group(1))
    
    return activities

def main():
    # File paths
    activities_yaml_path = 'data/activities.yaml'
    experiment_json_path = 'experiment_plans.json'
    output_txt_path = 'heterogeneity_metrics.txt'

    try:
        with open(activities_yaml_path, 'r') as f:
            all_activities_data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {activities_yaml_path}")
        return

    available_activities = {}
    for domain, acts_list in all_activities_data.items():
        names = []
        if isinstance(acts_list, list):
            for item in acts_list:
                # each item is a dict with one key (the activity name)
                if isinstance(item, dict):
                    names.extend(item.keys())
                elif isinstance(item, str):
                    names.append(item)
        available_activities[domain] = set(names)
    try:
        with open(experiment_json_path, 'r') as f:
            experiments = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {experiment_json_path}")
        return
    
    domain_counts = {d: Counter() for d in available_activities.keys()}
    
    for entry in experiments:
        plans = entry.get('plans', {})
        for domain in available_activities.keys():
            if domain in plans:
                plan_info = plans[domain]
                
                plan_str = plan_info.get('activity_plan', "")
                activities = parse_activity_plan(plan_str)
                
                # Update global counter
                domain_counts[domain].update(activities)

    lines_to_write = []
    lines_to_write.append("Heterogeneity Metrics for Activity Generation")
    lines_to_write.append("=============================================\n")
    lines_to_write.append("Metric Explanation:")
    lines_to_write.append("1. Entropy (bits): Shannon entropy of the activity distribution. Higher means more diverse.")
    lines_to_write.append("2. Normalized Entropy (0-1): Entropy divided by log2(Total Possible Activities). 1.0 means perfectly uniform distribution across all possible activities.\n")

    for domain in available_activities.keys():
        counts = domain_counts[domain]
        universe = available_activities[domain]
        universe_size = len(universe)
        
        # Identify activities that were never generated
        generated_set = set(counts.keys())
        unused = universe - generated_set
        
        entropy = calculate_entropy(counts)
        max_entropy = math.log2(universe_size) if universe_size > 0 else 0
        norm_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        
        lines_to_write.append(f"Domain: {domain.upper()}")
        lines_to_write.append(f"  - Total Possible Activities: {universe_size}")
        lines_to_write.append(f"  - Unique Activities Generated: {len(generated_set)}")
        lines_to_write.append(f"  - Unused Activities: {', '.join(unused) if unused else 'None'}")
        lines_to_write.append(f"  - Entropy: {entropy:.4f} bits")
        lines_to_write.append(f"  - Normalized Entropy: {norm_entropy:.4f}")
        lines_to_write.append("  - Distribution:")
        
        # Sort by frequency
        for act, count in counts.most_common():
            lines_to_write.append(f"    {act}: {count}")
        lines_to_write.append("")

    with open(output_txt_path, 'w') as f:
        f.write('\n'.join(lines_to_write))
    
    print(f"Metrics saved to {output_txt_path}")
    print("\nPreview of metrics:")
    print('\n'.join(lines_to_write[:20]))

if __name__ == "__main__":
    main()
