# project methods
import datetime
import os
from collections import defaultdict
import json
import cv2

from Defect_analyzer_back.resources.classes.coil import Coil
from Defect_analyzer_back.resources.model_utils import analyze_single_image
from Defect_analyzer_back.resources.config.configs_utils import get_current_config_json, create_folder_if_missing
from Defect_analyzer_front.run_frontend import app
from Defect_analyzer_front.defect_app import db
from Defect_analyzer_front.defect_app.models import Coil_post
from Defect_analyzer_back.resources.send_email import send_report


def save_output_image(image_np, image_path, coil_id):
    """ Saves the analyzed image into the output coil folder (containing the analyzed coil info)
        args:
            image_np: analyzed image in a numpy array
             image_path: path not-yet-analyzed image. From this the name of the image is obtained
             coil_id: name of the coil to which the image belongs. Used to generate the output folder name and path
        returns:
            True if the image was successfully saved
            False in opposite case.
    """

    if not os.path.isdir(get_current_config_json()['config']['path_to_output_folders']):
        os.makedirs(get_current_config_json()['config']['path_to_output_folders'])

    output_image_name = os.path.basename(image_path)
    output_folder_path = os.path.join(get_current_config_json()['config']['path_to_output_folders'],
                                      os.path.basename(os.path.dirname(image_path)) +
                                      get_current_config_json()['config']['output_folder_suffix'])
    output_image_path = os.path.join(output_folder_path, output_image_name)

    if not os.path.isdir(output_folder_path):
        os.makedirs(output_folder_path)

    if cv2.imwrite(output_image_path, image_np):
        print(f'\nImage {output_image_name} SAVED in {output_image_path}')
        return True
    else:
        print(f'Error while saving {output_image_name} in {output_image_path}')
        return False


def send_email_if_corresponds(coil):
    """ Evaluate thresholds and send email if overpassed """
    overpassed_categories = []

    def evaluate_thresholds():
        for category in coil.areas:
            if coil.areas[category] > get_current_config_json()['thresholds'][category]:
                overpassed_categories.append(category)
        if overpassed_categories:
            return True
        else:
            return False

    if evaluate_thresholds():
        receivers = [rx for rx in get_current_config_json()['emails']]
        message = f"Area Limite de los defectos: {overpassed_categories} superado." + f"{[categ + ' area: ' + str(int(coil.areas[categ])) + ' cm2 and the limit is: ' + str(get_current_config_json()['thresholds'][categ]) for categ in coil.areas]} "
        for mail_to in get_current_config_json()['emails'].split(','):
            send_report(subject='Aviso de limite de superficie superado',
                        body=message,
                        fromaddr='test@ternium.com.ar',
                        toaddr=mail_to,
                        filename='',
                        attachment_path='')


def analyze_coil_list(coil_list):
    """ Analyze each image of each coil
        args: coil list of coil-type elements"""

    def update_area_by_defect(image_boxes_json):
        """ Update the areas once an image is analyzed """
        for defect in image_boxes_json['detections']:
            post_json['areas'][defect['category']] += defect['area']

    def save_post_json_and_save_in_output_folder():
        post_json['coil'] = coil.__dict__
        path_to_post_json_folder = os.path.join(get_current_config_json()['config']['path_to_output_folders'],
                                                os.path.basename(coil.path) + get_current_config_json()['config'][
                                                    'output_folder_suffix'])
        path_to_post_json = os.path.join(path_to_post_json_folder, 'post.json')
        if not os.path.isdir(path_to_post_json_folder):
            os.makedirs(path_to_post_json_folder)
        with open(path_to_post_json, 'w') as f:
            json.dump(post_json, f, indent=2)
        return path_to_post_json

    def create_post_in_db_from_json():
        with app.app_context():
            coil_post = Coil_post(coil_id=coil.id, date=coil.date, time=coil.time, path=coil.path,
                                  areas=str(dict(coil.get_areas())))
            db.session.add(coil_post)
            db.session.commit()

    def analyze_coil_if_coildate_greaterthan_starting_date():
        # converting format to datetime
        date_to_compare_list = get_current_config_json()['config']['starting_date'].split('/')
        coil_date_to_compare_list = coil.date.split('/')
        d_comp = datetime.datetime(day=int(date_to_compare_list[2]), month=int(date_to_compare_list[1]),
                                   year=int(date_to_compare_list[0]))
        d_coil = datetime.datetime(day=int(coil_date_to_compare_list[0]), month=int(coil_date_to_compare_list[1]),
                                   year=int(coil_date_to_compare_list[2]))

        # comparison
        if d_coil >= d_comp:
            if coil.image_list:
                for image_path in coil.image_list:
                    # analyze image
                    output_image_np, image_boxes_json = analyze_single_image(image_path)
                    # update areas
                    update_area_by_defect(image_boxes_json)
                    # save image
                    if len(image_boxes_json['detections']):
                        save_output_image(output_image_np, image_path, coil.id)

    # .......................^ End of declarations ^...............................

    for coil in coil_list:
        post_json = defaultdict(
            lambda: defaultdict(float))  # post_json will contain all the necessary info to make a post in the frontend

        analyze_coil_if_coildate_greaterthan_starting_date()

        coil.set_areas_from_dict(post_json['areas'])
        send_email_if_corresponds(coil)
        add_coil_to_register(coil)
        path_to_post_json = save_post_json_and_save_in_output_folder()
        create_post_in_db_from_json()


def get_coils_in_register():
    """ Reads the register and returns a list with the coils in it
        args: register path (default register is set)
        return: coil object list """
    with open(get_current_config_json()['config']['path_to_current_coil_register_json']) as f:
        register = json.load(f)
    coils_in_register = json_to_coil_list(register) if register else []

    return coils_in_register  # list of Coil-type elements


def get_unregistered_coils_in_path(path=get_current_config_json()['config']['path_coils_folder']):
    """ Returns a dict containing the coils in the passed path, that are not in the register
        arg: path to the folder that contains coil folders
        returns None if there are no unregistered coils"""
    coils_in_register_list = get_coils_in_register()
    coils_in_path_list = get_coils_in_folder(get_current_config_json()['config']['path_coils_folder'])
    unregistered_coils_list = [coil_path for coil_path in coils_in_path_list if
                               all(coil_path.id != register_coil.id for register_coil in coils_in_register_list)]

    return unregistered_coils_list if len(unregistered_coils_list) else None


def json_to_coil_list(json_dict):
    """ Converts a dict (json) to a list of Coil objects
        arg: dict
        return: list of Coil objects"""
    return [Coil(coil['id'], coil['date'], coil['time'], coil['path'], coil['image_list']) for coil in
            json_dict['coils']]


def coil_list_to_json(coil_list):
    """ Takes a list of Coil objects and returns a defaultdict with the information
        args: coil object list
        return: defaultdict (json) with coil list info """
    coil_dict = defaultdict(list)
    for coil in coil_list:
        coil_dict['coils'].append({'id': coil.id,
                                   'date': coil.date,
                                   'time': coil.time,
                                   'path': coil.path,
                                   'image_list': coil.image_list})
    return coil_dict


def add_coil_to_register(coil):
    """ Appends the coil to the coil register
            arg: coil -> coil to append to the register """
    register_coils = get_coils_in_register()
    register_coils.append(coil)
    print('\nUpdating Register... ')
    update_coil_register(register_coils)
    print('Done')
    return True


def update_coil_register(coil_list):
    """ Create a JSON file containing the coils that are in the folder before the analysis starts.
        Those coils are not supposed to be analyzed
        args: Coil object list
        return: True if succeed in creating register"""

    if not os.path.isdir(get_current_config_json()['config']['path_to_current_coil_register_folder']):
        os.makedirs(get_current_config_json()['config']['path_to_current_coil_register_folder'])

    with open(get_current_config_json()['config']['path_to_current_coil_register_json'], 'w') as f:
        json.dump(coil_list_to_json(coil_list), f, indent=2)
        return True


def get_images_paths_in_path(path):
    """ return the paths of the images in the path. Possible extensions are specified in input_images_formats lists"""
    images_in_path = [os.path.join(path, file) for file in os.listdir(path) if
                      any(file.endswith(ext) for ext in
                          eval(get_current_config_json()['config']['input_images_formats']))]
    return images_in_path if len(images_in_path) else None


def create_coil_from_coil_path(coil_path):
    """ Create a Coil object from the coil path.
        args: coil_path
        return: coil object"""
    coil_data = os.path.basename(coil_path).split('-')  # coil_data example: [111111A, 1_ 1_2001, 13_ 2_20]
    coil_id = coil_data[0]

    dd = int(coil_data[1].split('_')[0])
    mm = int(coil_data[1].split('_')[1])
    yyyy = int(coil_data[1].split('_')[2])
    coil_date = datetime.date(yyyy, mm, dd).strftime('%d/%m/%Y')

    hh = int(coil_data[2].split('_')[0])
    mm = int(coil_data[2].split('_')[1])
    ss = int(coil_data[2].split('_')[2])
    coil_time = datetime.time(hh, mm, ss).strftime('%H:%M:%S')

    coil_images = get_images_paths_in_path(coil_path)

    coil = Coil(coil_id, coil_date, coil_time, coil_path, coil_images)

    return coil


def get_coils_in_folder(path):
    """Scans folders in the passed path, and check if are compatible with web inspector saving format

        args: path with coil folders
        return: list of Coil objects"""

    coil_list = []

    def check_web_inspector_format(item):
        """ check if the paths corresponds to a web inspector format folder"""
        if os.path.isdir(os.path.join(path,item)):  # is a dir
            if len(item.split('-')) == 3 and not any(
                    l for l in item if l in [':', ';', '.', ',']):
                return True
        else:
            return False

    def scan_path():
        def check_folder_date_conditions(coil_folder):
            """ Return True if the coil folder date satisfies the minor date in the config.
                Retrun False otherwise """

            folder_dd, folder_mm, folder_yyyy = [int(d) for d in item.split('-')[1].split('_')]
            folder_hour, folder_min, folder_sec = [int(d) for d in item.split('-')[1].split('_')]
            if folder_dd >= config_dd and folder_mm >= config_mm and folder_yyyy >= config_yyyy and folder_hour >= config_hour and folder_min >= config_min and folder_sec >= config_sec:
                return True
            else:
                return False

        # start
        print(f'Scanning {path} ...')

        # dates to compare with
        config_yyyy, config_mm, config_dd = [int(element) for element in get_current_config_json()['config']['starting_date'].split('/')]
        config_hour, config_min, config_sec = [int(element) for element in get_current_config_json()['config']['starting_time'].split(':')]

        # elements to evaluate (coil folders if they are so)
        elements_in_path = os.listdir(path)
        cant = len(elements_in_path)

        # path evaluation -> web inspector formatted & minimum date condition
        for i, item in enumerate(elements_in_path):
            if check_web_inspector_format(item) and check_folder_date_conditions(item):
                status = i * 100 / cant
                coil_list.append(create_coil_from_coil_path(os.path.join(path, item)))

                if not i % 100:
                    print(f'Scan Status {int(status)}%\tFiles: {i} of {cant}')
                if status >= 100:
                    print('Finish Scan')

    try:
        scan_path()
    except FileNotFoundError as e:
        print(f'ERROR: {e}\n')
        print('Creating Folder')
        create_folder_if_missing()
        scan_path()

    return coil_list
