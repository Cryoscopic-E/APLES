from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_cors import CORS
import csv
import os

app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes
app.secret_key = 'supersecretkey'  # Needed for flashing messages

# Define the path to the data folder and the CSV file
DATA_FOLDER = os.path.join(app.root_path, 'data')
APLES_FOLDER = os.path.join(app.root_path, 'aples')

from aples.aples_manager import create_level_structure

CSV_FILE = os.path.join(DATA_FOLDER, 'activities.csv')
GRAPH_CSV_FILE_PATH = os.path.join(DATA_FOLDER, 'levels.csv')
CSV_HEADERS = ['Activities', 'METScore', 'Type', 'Frequency', 'CurrentCost', 'CostIncrease', 'Steps', 'StepsAggregate']

# Ensure the CSV file exists with the correct headers and initialize from existing data if available
def initialize_csv():
    os.makedirs(DATA_FOLDER, exist_ok=True)
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
            writer.writeheader()

def read_csv():
    activities = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                activities.append(row)
    return activities

def write_csv(activities):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(activities)

def validate_activity(data):
    type_value = data.get('Type')
    steps = data.get('Steps')
    steps_aggregate = data.get('StepsAggregate')

    if type_value == 'Physical':
        if (steps and steps_aggregate) or (not steps and not steps_aggregate):
            flash('For Physical activities, either Steps or Steps Aggregate must be filled, but not both.', 'danger')
            return False
    elif type_value in ['Cognitive', 'Social']:
        if steps or steps_aggregate:
            flash('For Cognitive or Social activities, neither Steps nor Steps Aggregate should be filled.', 'danger')
            return False
    return True

def csvfromwebsite(activities):
    print("here")
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Activities', 'METScore', 'Type', 'Frequency', 'CurrentCost', 'CostIncrease', 'Steps', 'StepsAggregate'])
        for activity in activities:
            writer.writerow([activity['Activities'], activity['METScore'], activity['Type'], activity['Frequency'], activity['CurrentCost'], activity['CostIncrease'], activity['Steps'], activity['StepsAggregate']])

    # Save the graph data
    graph_data = request.json.get('graph', {})
    labels = graph_data.get('labels', [])
    datasets = graph_data.get('datasets', [])

    with open(GRAPH_CSV_FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['physical', 'social', 'cognitive'])

        for level in labels:
            physical = next((point['y'] for point in datasets[0] if point['x'] == level), 0)
            social = next((point['y'] for point in datasets[1] if point['x'] == level), 0)
            cognitive = next((point['y'] for point in datasets[2] if point['x'] == level), 0)
            writer.writerow([physical, social, cognitive])
    
    # planning shit
    create_level_structure(GRAPH_CSV_FILE_PATH, CSV_FILE)


    return jsonify({'status': 'success', 'message': 'CSV files saved successfully'})

# New API endpoint to serve activities data as JSON
@app.route('/activities', methods=['GET'])
def get_activities():
    activities = read_csv()
    return jsonify(activities)

@app.route('/')
def index():
    # The activities are no longer passed directly to the template
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_activity():
    new_activity = {
        'Activities': request.form.get('Activities', ''),
        'METScore': request.form.get('METScore', 0),
        'Type': request.form.get('Type', ''),
        'Frequency': request.form.get('Frequency', ''),
        'CurrentCost': request.form.get('CurrentCost', 0.0),
        'CostIncrease': request.form.get('CostIncrease', 0.0),
        'Steps': request.form.get('Steps', '') if request.form.get('Type') == 'Physical' else '',
        'StepsAggregate': request.form.get('StepsAggregate', '') if request.form.get('Type') == 'Physical' else ''
    }

    if validate_activity(new_activity):
        activities = read_csv()
        activities.append(new_activity)
        write_csv(activities)
        message = 'Activity added successfully!'
        return jsonify({'status': 'success', 'message': message})
    
    message = 'Validation failed!'
    return jsonify({'status': 'error', 'message': message}), 400

@app.route('/update/<int:index>', methods=['POST'])
def update_activity(index):
    activities = read_csv()
    if index < len(activities):
        updated_activity = {
            'Activities': request.form.get('Activities', ''),
            'METScore': request.form.get('METScore', 0),
            'Type': request.form.get('Type', ''),
            'Frequency': request.form.get('Frequency', ''),
            'CurrentCost': request.form.get('CurrentCost', 0.0),
            'CostIncrease': request.form.get('CostIncrease', 0.0),
            'Steps': request.form.get('Steps', '') if request.form.get('Type') == 'Physical' else '',
            'StepsAggregate': request.form.get('StepsAggregate', '') if request.form.get('Type') == 'Physical' else ''
        }

        if validate_activity(updated_activity):
            activities[index] = updated_activity
            write_csv(activities)
            message = 'Activity updated successfully!'
            return jsonify({'status': 'success', 'message': message})
    
    message = 'Failed to update activity!'
    return jsonify({'status': 'error', 'message': message}), 400

@app.route('/delete/<int:index>', methods=['POST'])
def delete_activity(index):
    activities = read_csv()
    if index < len(activities):
        activities.pop(index)
        write_csv(activities)
        message = 'Activity deleted successfully!'
        return jsonify({'status': 'success', 'message': message})
    
    message = 'Failed to delete activity!'
    return jsonify({'status': 'error', 'message': message}), 400


@app.route('/create_level', methods=['POST'])
def create_level():
    print("create level")
    activities = request.json.get('activities', [])
    return csvfromwebsite(activities)

if __name__ == '__main__':
    initialize_csv()
    app.run(debug=True, port=3002)
