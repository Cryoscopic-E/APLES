import json
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
website_root = os.path.abspath(os.path.join(current_dir, os.pardir))
apples_folder = os.path.join(website_root, 'aples')
configuration_json = os.path.join(apples_folder, 'data', 'minigame_config.json')

minigames = []

class minigame:
        def __init__(self, name, configuration):
                self.name = name
                self.configuration = configuration
                self.level = 0
                self.challenges = []

        def update_level(self, index):
                self.challenge = index
                current_level = self.level

                for ch in self.configuration[current_level]:
                    ch["challenge"] = index

                if self.level < len(self.configuration) - 1:
                        self.level = self.level + 1
                return self.configuration[current_level]



def create_minigames():
    with open(configuration_json, 'r') as file:
        configurations = json.load(file)
    confusing_arrows = minigame("confusing_arrows", configurations["confusing_arrows_config"])
    polygon_escape = minigame("polygon_escape", configurations["polygon_escape_config"])
    minigames.append(confusing_arrows)
    minigames.append(polygon_escape)

def minigame_update_level(name, index):
       minigame = get_minigame(name)
       return minigame.update_level(index)
       
def get_minigame(name):
       for minigame in minigames:
              if minigame.name == name:
                     return minigame
       return None
