from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import csv
import os
import requests


app = Flask(__name__)
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

@app.route('/')
def index():
    activities = read_csv()
    return render_template('index.html', activities=activities)

@app.route('/add', methods=['POST'])
def add_activity():
    new_activity = {
        'Activities': request.form['Activities'],
        'METScore': request.form['METScore'],
        'Type': request.form['Type'],
        'Frequency': request.form['Frequency'],
        'CurrentCost': request.form['CurrentCost'],
        'CostIncrease': request.form['CostIncrease'],
        'Steps': request.form['Steps'],
        'StepsAggregate': request.form['StepsAggregate']
    }

    if validate_activity(new_activity):
        activities = read_csv()
        activities.append(new_activity)
        write_csv(activities)
        flash('Activity added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/update/<int:index>', methods=['POST'])
def update_activity(index):
    activities = read_csv()
    if index < len(activities):
        updated_activity = {
            'Activities': request.form['Activities'],
            'METScore': request.form['METScore'],
            'Type': request.form['Type'],
            'Frequency': request.form['Frequency'],
            'CurrentCost': request.form['CurrentCost'],
            'CostIncrease': request.form['CostIncrease'],
            'Steps': request.form['Steps'] if request.form['Type'] == 'Physical' else '',
            'StepsAggregate': request.form['StepsAggregate'] if request.form['Type'] == 'Physical' else ''
        }

        if validate_activity(updated_activity):
            activities[index] = updated_activity
            write_csv(activities)
            flash('Activity updated successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:index>', methods=['POST'])
def delete_activity(index):
    activities = read_csv()
    if index < len(activities):
        activities.pop(index)
        write_csv(activities)
        flash('Activity deleted successfully!', 'success')
    return redirect(url_for('index'))


def cvsfromwebsite(activities):
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

@app.route('/create_level', methods=['POST'])
def create_level():
    print("create level")
    # Save the activities data
    activities = request.json.get('activities', [])
    return cvsfromwebsite(activities)
    # Here you'd normally prepare the data and make a request to the external API.
    print(activities)
    # Handle the response as needed
    flash('Level created successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    initialize_csv()
    app.run(debug=True)
