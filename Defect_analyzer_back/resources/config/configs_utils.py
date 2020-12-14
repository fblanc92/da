from Defect_analyzer_back.resources.config.config_initializer import path_to_current_config_folder, \
    path_to_default_config_json, \
    path_to_current_config_json
import json
import os
from datetime import datetime

def create_folder_if_missing(folderpath):
    try:
        if not os.path.isdir(folderpath):
            os.makedirs(folderpath)
        else:
            return
    except FileNotFoundError as e:
        print(f'No puede crearse la ruta {folderpath} como parametro de path_coil_folder')
        newpath = input('Ingrese una nueva ruta absoluta')
        with open(get_current_config_json()['config']['path_to_current_config_json']) as f:
            new_config = json.load(f)
            new_config['config']['path_coils_folder'] = newpath
        with open(get_current_config_json()['config']['path_to_current_config_json'], 'w') as g:
            json.dump(new_config, g, indent=2)
        if not os.path.isdir(newpath):
            create_folder_if_missing(newpath)


def get_current_config_json():
    """ :return an existing config dict from an existing config file """
    with open(path_to_current_config_json) as f:
        current_config_json = json.load(f)
    return current_config_json


def get_all_the_configs_list():
    """ Returns a list of dicts containing all the configs """

    def append_previous_configs_if_exist():
        path_to_previous_config_folder = current_config_json['config']['path_to_previous_config_folder']
        path_to_previous_config_file = current_config_json['config']['path_to_previous_config_file']
        path_to_current_config_json = current_config_json['config']['path_to_current_config_json']
        if path_to_previous_config_file != path_to_current_config_json:
            paths_to_previous_config_files = sorted([os.path.join(path_to_previous_config_folder, file) for file in
                                                     os.listdir(path_to_previous_config_folder)], reverse=True)
            for config_path in paths_to_previous_config_files:
                with open(config_path) as f:
                    config_list_to_return.append(json.load(f)['config'])

    current_config_json = get_current_config_json()

    # list that will contain all the config dicts ->
    # [ {key11: val11, key12: val12 ...}, {key21: val21, key22: val22, ...}, ... ]
    config_list_to_return = [current_config_json['config']]

    append_previous_configs_if_exist()

    return config_list_to_return


def update_config_date(config_json):
    config_json['config']['date_created'] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    return config_json


def update_config(config_dict):
    """ Makes the backup and config update of the config file keys using the config dict passed
        :arg config_dict : dict containing the key values to update
     """

    def save_current_config_file_into_previous_configs_folder():
        """ Makes the backup of the current config into the previous config folder,
            naming the file with date and time
            :return path to the saved config file
        """
        current_config_json = get_current_config_json()

        if not os.path.isdir(current_config_json['config']['path_to_previous_config_folder']):
            os.makedirs(current_config_json['config']['path_to_previous_config_folder'])

        sdatetime = current_config_json['config']['date_created'].replace('/', '_').replace(':', '_').replace(' ', '-')
        filepath_to_save = os.path.join(current_config_json['config']['path_to_previous_config_folder'],
                                        sdatetime + '.json')

        with open(filepath_to_save, 'w') as g:
            json.dump(current_config_json, g, indent=2, sort_keys=True)

        return filepath_to_save

    def update_config_values():
        """ Updates the current configuration using the config_dict passed to the parent function
            :return json type config variable: for writing the current config file
        """

        def create_folders_if_missing(json_config):
            """ Creates the folders of the new config that could be missing """
            for folder in [json_config['config']['path_coils_folder'], json_config['config']['path_to_output_folders']]:  #  path_to_output_folders is created in save_output_image
                if not os.path.isdir(folder):
                    os.makedirs(folder)

        print('Updating config.json')
        config_to_update_json = get_current_config_json()

        for conf in config_dict:
            try:
                if conf in ['input_image_formats']:
                    config_to_update_json['config'][conf] = eval(config_dict[conf])
                elif conf in ['scan_timer_delay', 'post_per_page']:
                    config_to_update_json['config'][conf] = int(config_dict[conf])
                elif conf in ['const_px_cm']:
                    config_to_update_json['config'][conf] = float(config_dict[conf])
                elif conf in ['thresholds']:
                    config_to_update_json['thresholds'] = eval(config_dict[conf])
                elif conf in ['emails']:
                    config_to_update_json['emails'] = config_dict[conf]
                else:
                    config_to_update_json['config'][conf] = config_dict[conf]

                print(f'Config value {conf} UPDATED')
            except KeyError as e:
                print(f'\n{conf} is not a valid config, {e}')

        config_to_update_json['config']['path_to_previous_config_file'] = previous_config_json_path
        config_to_update_json['config']['path_to_previous_config_folder'] = os.path.dirname(previous_config_json_path)

        # (Re)update date_created -> It was created first in the front end (Backend_config model) but
        # is useful to recreate it in the back when only running the backend
        config_to_update_json = update_config_date(config_to_update_json)

        create_folders_if_missing(config_to_update_json)

        return config_to_update_json

    def set_updated_config():
        """ Saves the updated configuration into the json config file """

        def recreate_register_if_changed():
            """ If the path to the register json file is changed, then creates the needed folder and
                recreates the current register json inside it """

            if 'path_to_current_coil_register_json' in config_dict:
                new_register_json_path = config_dict['path_to_current_coil_register_json']
                new_register_folder_path = os.path.dirname(new_register_json_path)
                if not os.path.isdir(new_register_folder_path):
                    os.makedirs(new_register_folder_path)

                with open(get_current_config_json()['config']['path_to_current_coil_register_json']) as f:
                    register_json = json.load(f)
                with open(new_register_json_path, 'w') as g:
                    json.dump(register_json, g, indent=2)

                print(f'Register Recreated In Location {new_register_json_path}')

        recreate_register_if_changed()  # if config_dict implies a change in the register location > recreate

        with open(get_current_config_json()['config']['path_to_current_config_json'], 'w') as f:
            json.dump(updated_config, f, indent=2)

    # Backup
    previous_config_json_path = save_current_config_file_into_previous_configs_folder()

    # Update parameters: config_dict -> current_config_dict
    updated_config = update_config_values()
    # Save new config.json
    set_updated_config()

    print(json.dumps(get_current_config_json(), indent=2, sort_keys=True))


def revert_config():
    def get_existing_config_json(config_path):
        with open(config_path) as f:
            config_json = json.load(f)
        return config_json

    def load_default_config():
        # Uses variables in config_initializer.py because it must load the default files that comes with the project
        with open(path_to_default_config_json) as f:
            default_config_json = json.load(path_to_default_config_json)
        with open(path_to_current_config_json, 'w') as f:
            json.dumps(default_config_json, f, indent=2)
        print('Default config loaded')

    current_config_json = get_current_config_json()
    path_to_previous_config_file = current_config_json['config']['path_to_previous_config_file']
    if os.path.isfile(path_to_previous_config_file):
        previous_config_dict = get_existing_config_json(path_to_previous_config_file)['config']
        update_config(previous_config_dict)
    else:
        print('No previous config found.')
        ans = input('Want to load the default config file?(y/n)')
        while ans not in ['n', 'N', 'y', 'Y']:
            ans = input('Enter a valid answer: y/n')
        if ans in ['y', 'Y']:
            load_default_config()
        elif ans in ['n', 'N']:
            print(
                f'Build a config.json file, like the following model, place it in {path_to_default_config_json} and try again')
            print(json.dump(path_to_default_config_json, indent=2, sort_keys=True))
