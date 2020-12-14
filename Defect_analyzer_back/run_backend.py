import threading
import json
from collections import defaultdict
from Defect_analyzer_back.resources.config.config_initializer import load_initial_config
from Defect_analyzer_back.resources.config.configs_utils import create_folder_if_missing

load_initial_config()

from Defect_analyzer_back.resources.coil_utils import get_coils_in_folder, update_coil_register, \
    get_unregistered_coils_in_path, analyze_coil_list

from Defect_analyzer_back.resources.config.configs_utils import get_current_config_json


def load_default_thresholds():
    path_to_labels_json = get_current_config_json()['config']['path_to_labels_json']
    default_thresholds_dict = defaultdict(lambda: defaultdict())
    with open(path_to_labels_json) as f:
        labels_json = json.load(f)
    for item in labels_json['items']:
        default_thresholds_dict[item['name']] = 1 * 10 ** 9
    with open(get_current_config_json()['config']['path_to_current_config_json']) as f:
        current_config_json = json.load(f)
        current_config_json['thresholds'] = default_thresholds_dict
    with open(get_current_config_json()['config']['path_to_current_config_json'],'w') as g:
        json.dump(current_config_json, g, indent=2)

def init_register():
    create_folder_if_missing(get_current_config_json()['config']['path_coils_folder'])
    coils_in_folder = get_coils_in_folder(get_current_config_json()['config']['path_coils_folder'])
    update_coil_register(coils_in_folder)


def start_app():
    """ Contains the app flow """

    current_config_json = get_current_config_json()
    unregistered_coils_list = get_unregistered_coils_in_path(current_config_json['config']['path_coils_folder'])
    if unregistered_coils_list:
        print(f'New unregistered folders {[coil.id for coil in unregistered_coils_list]}')
        analyze_coil_list(unregistered_coils_list)
    else:
        print('No new coils')

    app_timer = threading.Timer(current_config_json['config']['scan_timer_delay'], start_app).start()


def start_backend():
    # if __name__ == '__main__':
    init_register()
    load_default_thresholds()
    start_app()
