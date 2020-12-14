import json
import os
import datetime


def load_basic_configs_json():
    with open(r'C:\code\DA\Defect_analyzer_back\resources\defaults\basic_configs.json') as f:
        basic_configs_json = json.load(f)
    return [basic_configs_json['path_to_current_config_folder'],
            basic_configs_json['path_to_current_config_json'],
            basic_configs_json['path_to_default_config_json']]


def load_initial_config():
    """ :return default or an existing config dict"""

    def create_current_config_from_default():
        """ Creates a default config file when the current config file is missing
            :returns config dict with that info
        """
        with open(path_to_current_config_json, 'w') as f:
            with open(path_to_default_config_json) as g:
                current_config = json.load(g)
                current_config['config']['date_created'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                json.dump(current_config, f, indent=2, sort_keys=True)

        with open(path_to_current_config_json) as f:
            current_config = json.load(f)



        return current_config

    if not os.path.isdir(path_to_current_config_folder):
        os.makedirs(path_to_current_config_folder)

    if os.path.isfile(path_to_current_config_json):  # config file already exists -> read the config and return it
        with open(path_to_current_config_json) as f:
            current_config_json = json.load(f)
        return current_config_json
    else:
        return create_current_config_from_default()


path_to_current_config_folder, path_to_current_config_json, path_to_default_config_json = load_basic_configs_json()
