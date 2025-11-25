from yaml import safe_load

def main():
    with open('./data/activities.yaml') as activities_cfg:
        activites = safe_load(activities_cfg)
        print(activites.keys())



if __name__ == '__main__':
    main()