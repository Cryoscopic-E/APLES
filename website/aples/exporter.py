from collections import defaultdict
import copy
import datetime
import json
import math
import os
import random
import string
from openpyxl import load_workbook
import pandas as pd
from openpyxl.styles import numbers, Alignment
import requests
import re

from minigame import minigame_update_level

exported         = os.path.join(os.path.dirname(__file__), 'data', 'exported1.xlsx')
excel_data_path  = os.path.join(os.path.dirname(__file__), 'data', 'exampleactivities.csv')
csv_fluents_path = os.path.join(os.path.dirname(__file__), 'data', 'fluents.csv')
sheet_data_path  = os.path.join(os.path.dirname(__file__), 'data', 'sheet1.csv')
sheet2_data_path = os.path.join(os.path.dirname(__file__), 'data', 'sheet2.csv')

# HARDCODED VIDEO URLS - VIDEOS ARE FOUND IN THE "media-for-ai" CAMPAIGN
# video_urls = {
#     'tutorial_video(cognitive_activity)' : 'https://campaigns.healthyw8.gamebus.eu/api/media/generated-296ffd13/66972617-5cd5-40e1-8432-ecd99b7dcf10.h5p',
#     'tutorial_video(physical_activity)'  : 'https://campaigns.healthyw8.gamebus.eu/api/media/generated-296ffd13/a4466cf8-adb1-4a54-9e56-075eae837a53.h5p',
#     'tutorial_video(social_activity)'    : 'https://campaigns.healthyw8.gamebus.eu/api/media/generated-296ffd13/f0a366cc-c574-4807-8dab-5dd53dd47f70.h5p',
#     'tutorial_video(minigame_activity)'    : 'https://campaigns.healthyw8.gamebus.eu/api/media/media-for-ai/08e5d4bd-a41d-425d-9fd0-c5954205076d.h5p'
#     }
#Localhost
video_urls = {
    'tutorial_video(cognitive_activity)' : 'http://localhost:5173/api/media/media-for-ai-b7b4437a/a6cf16fb-1b3c-4862-9086-307cb11c2a41.h5p',
    'tutorial_video(physical_activity)'  : 'http://localhost:5173/api/media/media-for-ai-b7b4437a/bb7ce12e-3542-4874-b236-6f4d26bb3a4c.h5p',
    'tutorial_video(social_activity)'    : 'http://localhost:5173/api/media/media-for-ai-b7b4437a/b7fb3d01-9712-476f-9d53-4876283c73ce.h5p',
    'tutorial_video(minigame_activity)'    : 'http://localhost:5173/api/media/media-for-ai-b7b4437a/ba5eb809-ed8e-4688-acb0-0df598a2c57c.h5p'
    }

def update_paths_exporter(exported_file, activities):
    global exported        
    global excel_data_path
    exported = exported_file
    excel_data_path = activities    


def export_to_excel():
    df = pd.read_csv(sheet_data_path)
    writer = pd.ExcelWriter(exported, engine='openpyxl', mode='a', if_sheet_exists='replace')
    df.to_excel(writer, sheet_name='tasks', index=None)
    writer.close()
    
    df = pd.read_csv(sheet2_data_path)

    with pd.ExcelWriter(exported, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name='challenges', index=False)
        workbook = writer.book
        s = workbook['tasks']
        
        for cell in s[1]:
            cell.style = 'Normal'

    with pd.ExcelWriter(exported, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name='challenges', index=False)

        workbook = writer.book
        s = workbook['challenges']
        
        for cell in s[1]:
            cell.style = 'Normal'

        first_h = True
        for cell in s["H"]:
            if first_h == False:
                cell.value = datetime.datetime.strptime('2025-01-01 6:00', '%Y-%m-%d %H:%M')
                cell.number_format = 'yyyy-mm-dd hh:mm'
            first_h = False
        
        first_g = True
        for cell in s["G"]:
            if first_g == False:
                cell.value = '122'
                cell.number_format = numbers.FORMAT_TEXT
            first_g = False   

        first_s = True
        for cell in s["I"]:
            if first_s == False:
                cell.value = datetime.datetime.strptime('2025-07-01 6:00', '%Y-%m-%d %H:%M')
                cell.number_format = 'yyyy-mm-dd hh:mm'
            first_s = False

def empty_sheets():
    df = pd.read_csv(sheet_data_path)
    df = pd.DataFrame(df.head(0))
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df.to_csv(sheet_data_path, index=False)
    df = pd.read_csv(sheet2_data_path)
    df = pd.DataFrame(df.head(0))
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df.to_csv(sheet2_data_path, index=False)

def random_secret():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(10,50)))

def append_row_to_sheet(index, name, met_score, frequency, steps = '', steps_aggregate = '', activity_type =''):
    df = pd.read_csv(sheet_data_path)
    h5p_slug = ''
    conditions = ''

    if type(steps) == int:
        activity_scheme = 'WALK'
        conditions = '[STEPS, STRICTLY_GREATER, {}],'.format(steps)
    elif type(steps_aggregate) == int:
        activity_scheme = 'DAY_AGGREGATE'
        conditions = '[STEPS_SUM, STRICTLY_GREATER, {}],'.format(steps_aggregate)
    else:
        activity_scheme = 'GENERAL_ACTIVITY'

    if "tutorial" in name:
        activity_scheme = 'H5P_GENERAL'
        h5p_slug = video_urls.get(name)

    if activity_type == "minigame":
        minigame_configuration = minigame_update_level(name.lower(), index)
        df = pd.concat([df, pd.DataFrame(minigame_configuration)], ignore_index=True)
        df.to_csv(sheet_data_path, index=False)
    else:
        conditions += ' [SECRET, EQUAL, {}]'.format(random_secret())

        new_row = {
            'challenge': index,
            'name': '{}'.format(name),
            'description': '',
            'image': 'https://campaigns.healthyw8.gamebus.eu/api/media/HW8-immutable/5ff935d3-d0ae-4dce-bfcd-d2f71bf2ca63.jpeg',
            'video': '',
            'h5p_slug': '{}'.format(h5p_slug),
            'max_times_fired': frequency,
            'min_days_between_fire': '7',
            'activityscheme_default': '{}'.format(activity_scheme),
            'activityschemes_allowed': '{}'.format(activity_scheme),
            'image_required': '0',
            'conditions': '{}'.format(conditions),
            'points': met_score,
            'dataproviders': 'GameBus Studio'
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(sheet_data_path, index=False)


def append_level_to_sheet(index, target, success_next = -1, failure_next = -1):
    current_level_ = index
    df = pd.read_csv(sheet2_data_path)
    if current_level_ == 1:
        is_initial_level = 1
    else:
        is_initial_level = 0

    new_row = {
        'campaign': 17,
        'id': current_level_,
        'type': 'TASKS_COLLECTION',
        'name': 'G{}'.format(current_level_),
        'image': 'https://campaigns.healthyw8.gamebus.eu/api/media/HW8-immutable/3ad4d1db-b854-45cb-bcef-59dbaee47f6e.jpeg',
        'description': 'Generated by AI',
        'visualizations': '122',
        'start': datetime.datetime.strptime('2025-01-01 6:00', '%Y-%m-%d %H:%M'),
        'end': datetime.datetime.strptime('2025-07-01 6:00', '%Y-%m-%d %H:%M'),
        'contender': '',
        'is_initial_level': is_initial_level,
        'target': target,
        'success_next': success_next,
        'evaluate_fail_every_x_minutes': '10080',
        'failure_next': failure_next
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(sheet2_data_path, index=False)

def get_executed_actions(plan):
    executed_actions = []
    lines = str(plan).splitlines()
    for line in lines:
        line = line.strip()
        if line and not line.endswith(':'):
            action_name = line
            if "tutorial" not in action_name:
                action_name = action_name.split('(')[0] 
            executed_actions.append(action_name)
    return executed_actions

def reset_fluents_csv():
    df = pd.read_csv(csv_fluents_path)
    df['status'] = False
    df.to_csv(csv_fluents_path, index=False)


def update_fluents_csv(plan):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_fluents_path)
    
    # Convert the plan to a list of actions
    plan_string = str(plan).splitlines()
    
    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        object_type_name = row['name']
        object_type_status = row['status']
        
        # Iterate over each action in the plan
        for action in plan_string:
            match = re.search(r'\(([^)]+)\)', action)
            if match:
                action_type = match.group(1)
                # Update the DataFrame directly
                if object_type_name == action_type and object_type_status == False:
                    df.at[index, 'status'] = True

    # Save the updated DataFrame back to the CSV file
    df.to_csv(csv_fluents_path, index=False)

def export_plan_to_sheet(index, p):
    actions = get_executed_actions(p)
    update_fluents_csv(p)
    df_actions = pd.read_csv(excel_data_path)
    local_level = index
    tut = False
    for a in actions:
        match = df_actions[df_actions['Activities'] == a]

        if "tutorial" in a:
            if tut == False:
                local_level = local_level + 1
            append_row_to_sheet(local_level, a, 1, 1)
            local_level = local_level + 1
            tut = True

        elif not match.empty:
            steps = ''
            steps_aggregate = ''
            activityname = match['Activities'].values[0]
            if not math.isnan(match['Steps'].values[0]):
                steps = int(match['Steps'].values[0])

            if not math.isnan(match['StepsAggregate'].values[0]):
                steps_aggregate = int(match['StepsAggregate'].values[0])

            append_row_to_sheet(local_level, activityname, match['METScore'].values[0], 1, steps, steps_aggregate, match['Type'].values[0])
            tut = False

    return local_level + 1

def create_levels():
    actions = pd.read_csv(sheet_data_path)
    levels_list = []

    for a in actions['challenge']:
        levels_list.append(a)
    levels_list = list(dict.fromkeys(levels_list))


    for index, l in enumerate(levels_list):
        current_target = 0
        #Determine the target points of the level
        for i, a in actions.iterrows():
            if a['challenge'] == l :
                current_target += a['points']

        if (l + 1) in levels_list:
            success_next = levels_list[index + 1]
        else:
            success_next = -1

        if (l - 1) in levels_list:
            failure_next = levels_list[index - 1]
        else:
            failure_next = -1
        
        append_level_to_sheet(l, current_target, success_next, failure_next)
    
    df = pd.read_csv(sheet2_data_path)
    if df.iloc[0]["failure_next"] == -1:
        df.at[0, "failure_next"] = ''
    if df.iloc[0]["success_next"] == -1:
        df.at[0, "success_next"] = ''

    if df.iloc[-1]["failure_next"] == -1:
        df.at[df.index[-1], "failure_next"] = ''
    if df.iloc[-1]["success_next"] == -1:
        df.at[df.index[-1], "success_next"] = ''

    df.to_csv(sheet2_data_path, index=False)

def push_to_gamebus():
    writer = pd.ExcelWriter(exported, engine='openpyxl', mode='a', if_sheet_exists='replace')
    writer.close()

    #production
    # url = "https://campaigns.healthyw8.gamebus.eu/api/campaigns/upload"
    
    #local version
    url = "http://localhost:5173/api/campaigns/upload"

    payload = {}
    files=[
    ('file',('exported1.xlsx',open(exported,'rb'),'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
    ]
    headers = {
    'accept': '*/*',
    'accept-language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
    'cookie': '__session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MywiZW1haWwiOiJsLmouamFtZXNAdHVlLm5sIiwiaWF0IjoxNzM0NDMyNjYxLCJleHAiOjE3NDIyMDg2NjF9.yrQkvCC-vT5ZKE3u_7ZI77PzFu6lTx1EKK6REDQymso',
    'dnt': '1',
    # 'origin': 'https://campaigns.healthyw8.gamebus.eu',
    'origin': 'http://localhost:5173',
    'priority': 'u=1, i',
    # 'referer': 'https://campaigns.healthyw8.gamebus.eu/editor/campaigns',
    'referer': 'http://localhost:5173/editor/campaigns',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36'
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    print(response.status_code)
    print(response.text)
    print(response)

    data = json.loads(response.text)
    campaign_id = data[0]["id"]
    activate_campaign(campaign_id)

def activate_campaign(campaign_id):
    #production version
    # url = "https://campaigns.healthyw8.gamebus.eu/editor/campaigns/{}".format(campaign_id)
    #local version 
    url = "http://localhost:5173/editor/campaigns/{}".format(campaign_id)

    payload = '__superform_json=%5B%7B%22abbreviation%22%3A1%2C%22name%22%3A2%2C%22description%22%3A3%2C%22logo%22%3A4%2C%22start%22%3A5%2C%22end%22%3A6%2C%22contact_person%22%3A7%2C%22contact_email%22%3A8%2C%22organizers%22%3A9%2C%22viewers%22%3A11%7D%2C%22generated-3ca73483%22%2C%22Upload%20of%20An%20AI-Planning%20Generated%20campaign%22%2C%22This%20campaign%20is%20the%20testing%20ground%20of%20an%20AI%20system%22%2C%22https%3A%2F%2Fcampaigns.healthyw8.gamebus.eu%2Fapi%2Fmedia%2FHW8-immutable%2Ffebe6f8e-5025-4887-a934-9dbec31cf4d8.svg%22%2C%5B%22Date%22%2C%222025-01-01T18%3A15%3A00.000Z%22%5D%2C%5B%22Date%22%2C%222025-07-01T18%3A16%3A00.000Z%22%5D%2C%22Lorenzo%20James%22%2C%22l.j.james%40tue.nl%22%2C%5B10%5D%2C14%2C%5B%5D%5D&__superform_id=1jic8px'
    headers = {
    'accept': 'application/json',
    'accept-language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded',
    'cookie': '__session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTQsImVtYWlsIjoibC5qLmphbWVzQHR1ZS5ubCIsImlhdCI6MTcyMjMyNjg5NiwiZXhwIjoxNzMwMTAyODk2fQ.uWOPSz8UNnehYFV92NRbj61p4PYY-X2VZmBHsaoT5-g',
    'dnt': '1',
    # 'origin': 'https://campaigns.healthyw8.gamebus.eu',
    'origin': 'http://localhost:5173',
    'priority': 'u=1, i',
    # 'referer': 'https://campaigns.healthyw8.gamebus.eu/editor/campaigns/{}'.format(campaign_id),
    'referer': 'http://localhost:5173/editor/campaigns/{}'.format(campaign_id),
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    'x-sveltekit-action': 'true'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


