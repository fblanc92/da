import numpy as np
import os
import six.moves.urllib as urllib
import sys
# import tarfile
import tensorflow as tf
# import zipfile
import cv2
import pandas as pd
import datetime
from distutils.version import StrictVersion
from collections import defaultdict
from io import StringIO
import tkinter

import openpyxl

import matplotlib
# matplotlib.use('Qt5Agg')
from time import sleep
import threading
# matplotlib.use('tkAgg')
# input('%matplotlib inline')
from matplotlib import pyplot as plt

plt.rcParams.update({'figure.max_open_warning': 0})
plt.ion()
from object_detection.utils import label_map_util

# from object_detection.utils import visualization_utils as vis_util
os.chdir(r'C:\Users\fblanc.TERNIUM\Desktop\TERNIUM\Python3\ML')
# SMTP server
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# images
from resources import visualization_utils_fb as vis_util
from PIL import Image
import logging

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")
from resources.object_detection.utils import ops as utils_ops

if StrictVersion(tf.__version__) < StrictVersion('1.12.0'):
    raise ImportError('Please upgrade your TensorFlow installation to v1.12.*.')

from resources import sgl

# %%
# Basic config - Selecting directories & globals

# 
PATH_TO_FROZEN_GRAPH = 'C:/tensorflow/tuto/models/research/object_detection/graph_ssd/frozen_inference_graph.pb'
PATH_TO_LABELS = 'C:/tensorflow/tuto/models/research/object_detection/training/labelmap.pbtxt'
# Other paths
# PATH_SHARED = r'\\172.17.30.23\Informes'
PATH_SHARED = r'C:\test'
PATH_BOBINA_ACTUAL = os.path.join(PATH_SHARED, 'BobinaActual')
PATH_ANALYZED = os.path.join(PATH_SHARED, 'Analyzed_tmp')
# Logging config
logging.basicConfig(level=logging.DEBUG, filename='logger.log', filemode='a',
                    format='%(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# globals
files = []  # to use in check()
IMAGE_SIZE = (12, 8)  # to plot in analyze()
boxes = []  # to get the boxes data from vis_utils in analyze()
lista_temp = []
# Advice variables
warn_deleted = False
warn_created = True
boxes_df = pd.DataFrame()
# %% TensorFlow graph
detection_graph = tf.Graph()

with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)


def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)


def run_inference_for_single_image(image, graph):
    with graph.as_default():
        # with tf.Session() as sess:
        with tf.compat.v1.Session() as sess:
            # ops = tf.get_default_graph().get_operations()
            ops = tf.compat.v1.get_default_graph().get_operations()
            all_tensor_names = {output.name for op in ops for output in op.outputs}
            tensor_dict = {}
            for key in [
                'num_detections', 'detection_boxes', 'detection_scores',
                'detection_classes', 'detection_masks'
            ]:
                tensor_name = key + ':0'
                if tensor_name in all_tensor_names:
                    tensor_dict[key] = tf.compat.v1.get_default_graph().get_tensor_by_name(
                        tensor_name)
            if 'detection_masks' in tensor_dict:
                detection_boxes = tf.sueeze(tensor_dict['detection_boxes'], [0])
                detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
                real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
                detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                    detection_masks, detection_boxes, image.shape[1], image.shape[2])
                detection_masks_reframed = tf.cast(
                    tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                tensor_dict['detection_masks'] = tf.expand_dims(
                    detection_masks_reframed, 0)
            image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

            # Run inference
            output_dict = sess.run(tensor_dict,
                                   feed_dict={image_tensor: image})

            # all outputs are float32 numpy arrays, so convert types as appropriate
            output_dict['num_detections'] = int(output_dict['num_detections'][0])
            output_dict['detection_classes'] = output_dict[
                'detection_classes'][0].astype(np.int64)
            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
            output_dict['detection_scores'] = output_dict['detection_scores'][0]
            if 'detection_masks' in output_dict:
                output_dict['detection_masks'] = output_dict['detection_masks'][0]
    return output_dict


# %%
def clean_boxes_df():
    global boxes_df, columns
    boxes_df = pd.DataFrame(columns=columns)


# %%
def send_report(subject='',
                body='',
                fromaddr='test@ternium.com.ar',
                toaddr='fblanc@ternium.com.ar',
                filename='Defectos.xlsx',
                attachment_path=''):
    # instance of MIMEMultipart
    msg = MIMEMultipart()
    # storing the senders email address
    msg['From'] = fromaddr
    # storing the receivers email address
    msg['To'] = toaddr
    # storing the subject
    msg['Subject'] = subject
    # string to store the body of the mail
    body = body
    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))
    # open the file to be sent
    attachment = open(attachment_path, 'rb')
    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')
    # To change the payload into encoded form
    p.set_payload((attachment).read())
    # encode into base64
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    # attach the instance 'p' to instance 'msg'
    msg.attach(p)
    # creates SMTP session
    s = smtplib.SMTP('10.210.23.72', 25)
    s.ehlo()
    # start TLS for security
    s.starttls()
    s.ehlo()
    # Converts the Multipart msg into a string
    text = msg.as_string()
    # sending the mail
    s.sendmail(fromaddr, toaddr, text)
    # terminating the session
    s.quit()


# %%
FLAG_EXCEL_WI_READY = False


def export_data(path_last_coil):
    global PATH_ANALYZED
    global boxes_df, columns
    # ============== PATHS ===============

    xlsx_name = 'Analysis.xlsx'
    # csv_name = 'csv.csv'
    histogram_name = 'histogram.png'
    # PATH_XLSX = os.path.join(PATH_ANALYZED,xlsx_name)
    PATH_XLSX = os.path.join(path_last_coil, xlsx_name)
    # CSV_PATH = os.path.join(PATH_ANALYZED,csv_name)
    HISTOGRAM_PATH = os.path.join(path_last_coil, histogram_name)

    # ============== FLAGS ===============

    # PATH_XLSX
    FLAG_XLSX_EXISTS = True if os.path.isfile(PATH_XLSX) else False

    # File writer
    if not FLAG_XLSX_EXISTS:
        writer = pd.ExcelWriter(PATH_XLSX, engine='xlsxwriter')
        boxes_df.to_excel(writer,
                          index=False,
                          header=True,
                          columns=columns,
                          sheet_name='Coil Data')
        writer.save()
        writer.close()

        # ================ plots ================
        # images creation
        histogram = boxes_df.Categ.hist().get_figure()
        histogram.tight_layout(pad=0.4)
        histogram.savefig(HISTOGRAM_PATH)

        histogram = openpyxl.drawing.image.Image(HISTOGRAM_PATH)

        histogram.width = histogram.width / 2
        histogram.height = histogram.height / 2

        # ============ Append plots to xlsx ===========
        # workbook & worksheet
        workbook = openpyxl.load_workbook(PATH_XLSX)

        ws_charts = workbook.create_sheet('Coil Charts')
        histogram.anchor = 'A2'
        ws_charts.add_image(histogram)

        workbook.save(PATH_XLSX)


# %% Manage folders in sharedFolder
# use PATH_SHARED
coil_register = []  # stores the whole list of coils to avoid processing the same coil folder twice


def scan_folders(PATH=PATH_SHARED):
    global coil_register, folder_str
    folders = []
    folder_columns = ['ID', 'Date', 'Time']
    scan = os.listdir(PATH)
    FLAG_REPEATED_COIL = False
    for fldr in scan:
        if os.path.isdir(os.path.join(PATH, fldr)):
            folderName = fldr.split('-')
            if len(folderName) == 3:

                coil_ID = folderName[0]

                FLAG_REPEATED_COIL = True if coil_ID in coil_register else False
                if not FLAG_REPEATED_COIL:
                    coil_register.append(coil_ID)
                    # print('coil id:',coil_ID)
                    DD = int(folderName[1].split('_')[0])
                    MM = int(folderName[1].split('_')[1])
                    YYYY = int(folderName[1].split('_')[2])
                    coil_date = datetime.date(YYYY, MM, DD).strftime('%d/%m/%Y')

                    HH = int(folderName[2].split('_')[0])
                    MM = int(folderName[2].split('_')[1])
                    SS = int(folderName[2].split('_')[2])
                    coil_time = datetime.time(HH, MM, SS)

                    folders.append([coil_ID, coil_date, coil_time])
                    folder_str = fldr

    folder_df = pd.DataFrame(folders, columns=folder_columns).sort_values(by=['Date', 'Time'], ascending=[False, False])
    folder_df.reset_index(drop=True, inplace=True)
    return folder_df, folders


# %%
THRESH_AB1 = 20


def eval_thresholds(folder):
    # evaluate conditions for sending report
    global THRESH_AB1, boxes_df
    cm2_ab1 = boxes_df['cm2 Area'][boxes_df['Categ'] == 'ab1'].sum()
    # FLAG_AREA_EXCEEDED
    FLAG_AB1_EXEEDED = True if cm2_ab1 > THRESH_AB1 else False

    print('*Evaluating defect thresholds')

    if FLAG_AB1_EXEEDED:
        print('*ADVICE: AB-1 Threshold (', THRESH_AB1, '<', cm2_ab1, ') exeeded')
        print('*ADVICE: Sending Coil Report')

        PATH_ATTACHMENT = os.path.join(PATH_SHARED, folder, 'excel.xlsx')
        print('**Looking for xlsx ', PATH_ATTACHMENT)
        #    send_report('Informe Defect Analyzer - TRL',
        #                  'Este es un informe de defectos de TRL',
        #                  'DefectAnalyzer-TRL@ternium.com.ar',
        #                  'fblanc@ternium.com.ar',
        #                  'Defectos.xlsx',
        #                  PATH_ATTACHMENT)
        print('*REPORT SENT')


# %%
def print_accumulated_areas():
    global boxes_df
    categs = ['ab2', 'ab1', 'ab0', 'abb', 'pl2', 'pl1', 'pl0', 'pls', 'co0', 'co1', 'co2', 're', 'res', 'sol', 'ag0',
              'ag1', 'ag2', 'vibracion', 'm', 'mb', 'abr']
    cm2_by_categ = []
    for category in categs:  # from labelmap
        area = boxes_df['cm2 Area'][boxes_df['Categ'] == category].sum()
        cm2_by_categ.append(area)

    print('\t___ Accumulated_Defect_Area[cm2] ___')
    for i, cm2 in enumerate(cm2_by_categ):
        print('\t', categs[i], '\t\t', cm2)


# %% folder_df (DataFrame) will be get from the fist scan and is going to be de reference of the comparison
# folder_list_tmp (DataFrame) will be get from the preriodic scan, every x time and will be compared with folder_df,
# the differences are the new folders
def get_new_coil_name():
    global folder_list_tmp
    global folder_df
    global fl  # folder list scanned at the beggining  or updated in this function
    global FLAG_NEW_COIL_FOLDER
    new_coil_name = ''
    # ============= scan looking for new folders
    folder_list_tmp, fl_tmp = scan_folders(PATH_SHARED)
    # print(folder_list_tmp)
    if os.path.isdir(PATH_ANALYZED) and not FLAG_NEW_COIL_FOLDER:
        for folder_in_fl in fl_tmp:
            if folder_in_fl not in fl:
                # format new coil folder soit is the name of the new folder (now it is splitted)
                new_coil_name = folder_in_fl[0].split('-')[0]
                print('*New Coil: ', new_coil_name)
                FLAG_NEW_COIL_FOLDER = True

        # update lists
        fl = fl_tmp
        folder_df = folder_list_tmp

        return new_coil_name


#    if new_analysis_folder_name.isalnum:
#      return new_analysis_folder_name,True # second valiue indicates is alphanum
#    else:
#      return 'NOCOIL',False
# %%
def format_boxes_data(boxes_df_tmp):
    # ============== boxes normalization =================
    # global columns
    # global boxes_df

    for row in range(len(boxes_df_tmp)):
        Date_formated = (
            ((((str(boxes_df_tmp['Date'][row])).replace(',', '/')).replace('[', '')).replace(']', '')).replace('\'',
                                                                                                               '')).replace(
            ' ', '')
        Time_formated = (
            (((str(boxes_df_tmp['Time'][row]).replace(',', ':')).replace('[', '')).replace(']', '')).replace('\'',
                                                                                                             '')).replace(
            ' ', '')
        Coordinates_formated = ((str(boxes_df_tmp['Coordinates'][row])).replace('[', '')).replace(']', '')

        boxes_df_tmp['Date'][row] = Date_formated
        boxes_df_tmp['Time'][row] = Time_formated
        boxes_df_tmp['Coordinates'][row] = Coordinates_formated

    return boxes_df_tmp


# %%
def save_img(img_np, img_path):
    img_name = os.path.basename(img_path)  # path untill ...Defecto.png
    global PATH_ANALYZED
    FLAG_ANALYZED_FOLDER_CREATED = True if os.path.isdir(PATH_ANALYZED) else False
    if not FLAG_ANALYZED_FOLDER_CREATED:
        os.makedirs(PATH_ANALYZED)
        print('*CREATED Analized_tmp folder')
    new_img_path = os.path.join(PATH_ANALYZED, '_analyzed_' + img_name)
    cv2.imwrite(new_img_path, img_np)
    print('*Saved: Analyzed Image', img_name)
    return


# %% add_image_column: adds the column that indicates from what image the boxes were obtained
def add_image_column(image_path, boxes_df_tmp):
    image_name = os.path.basename(image_path)
    image_column_list = []  # this list will contain the image name, and will be appended to boxes_df

    for i in range(len(boxes_df_tmp)):
        image_column_list.append(image_name)
    # print('len(boxes_df_columns)',len(boxes_df_tmp.columns), 'image_column_list',image_column_list)

    boxes_df_tmp['Image'] = image_column_list

    return boxes_df_tmp


# %%
def complete_boxes_df_tmp_columns(boxes_df_tmp):
    init_cant_cols = len(boxes_df_tmp.columns)
    if not init_cant_cols == len(columns):
        difference = len(columns) - init_cant_cols
        for col in range(difference):
            boxes_df_tmp[init_cant_cols + col] = ''
    boxes_df_tmp.columns = columns
    return boxes_df_tmp


# %%
def analyze(image_path):
    global boxes
    global boxes_df

    image = Image.open(image_path).convert('RGB')

    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    res_w = 800
    res_h = 595
    image = image.resize((res_w, res_h))

    image_np = load_image_into_numpy_array(image)
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    # Actual detection.
    output_dict = run_inference_for_single_image(image_np_expanded, detection_graph)
    # Visualization of the results of a detection.

    image_np, boxes = vis_util.visualize_boxes_and_labels_on_image_array(
        # WARNING: visualization_utils must be corrected
        image_np,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        category_index,
        instance_masks=output_dict.get('detection_masks'),
        use_normalized_coordinates=True,
        line_thickness=1)
    plt.figure(figsize=IMAGE_SIZE)
    plt.gcf().canvas.set_window_title(image_path)

    print('*Analyzing file', image_path)

    # convert the returned

    boxes_df_tmp = pd.DataFrame(data=boxes)  # not adding column names yet because is not complete (still 8 cols)

    # delete boxes
    boxes = []

    # complete temp dataframe columns to allow name assignment
    boxes_df_tmp = complete_boxes_df_tmp_columns(boxes_df_tmp)
    #    init_cant_cols = len(boxes_df_tmp.columns)
    #    if not init_cant_cols == len(columns):
    #      difference = len(columns)-init_cant_cols
    #      for col in range(difference):
    #        boxes_df_tmp[init_cant_cols+col]=''
    #    boxes_df_tmp.columns = columns

    # add image name info to temp dataframe
    boxes_df_tmp = add_image_column(image_path, boxes_df_tmp)

    # format date, time and coords
    boxes_df_tmp = format_boxes_data(boxes_df_tmp)  # Date | Time | Coordinates

    # add recent analysis to the coil analysis
    boxes_df = pd.concat([boxes_df, boxes_df_tmp], ignore_index=True)

    # reset the boxes obtained from current image analysis
    del (boxes_df_tmp)

    # save image
    save_img(image_np, image_path)

    # show accumulated areas by categ
    print_accumulated_areas()

    return


# %% add_position column => appends the meters column from the webinspector xls to the boxes_df
# input_df: webinspector, process_df: boxes_df
def add_position_column(input_df, process_df):
    process_df.sort_values(by=['Image'], axis='index', ascending=True, inplace=True)
    process_df.reset_index(drop=True, inplace=True)
    # Getting the position of every defect
    defect_and_position = []
    print('\t___ Defect_Positions ___')
    for index in range(len(input_df)):

        position = input_df['Posición [m]'][index]
        photonum = input_df['Nº Foto'][index]
        FLAG_IS_NAN = np.isnan(photonum)
        if not FLAG_IS_NAN:

            defectnum = 'Defecto-' + str(int(photonum)) + '.png'
            if index > 0:

                photonum_prev = input_df['Nº Foto'][index - 1]
                if not photonum == photonum_prev:
                    print('\t', index, position, defectnum)
            else:

                print('\t', index, position, defectnum)

            defect_and_position.append([defectnum, position])

    # Appending values to the process dataframe
    column_to_append = []  # this will contain Defecto-X.png meters with correct index
    # ===== column_to_append =====
    # [Defecto-1.png    80.0]
    # [Defecto-1.png    80.0]
    # ...
    # [Defecto-x.png    3420.0]
    #
    for defect_position in defect_and_position:
        defect = defect_position[0]
        meters = defect_position[1]

        for i, index in process_df.iterrows():
            if index['Image'] == defect:
                column_to_append.append(meters)

    # print('COLUMN\n',column_to_append)
    print('\n\n process_df:\n', process_df, '\n\n column to append\n', column_to_append)
    process_df['Position[m]'] = column_to_append

    # print(process_df)

    return process_df


# %%
FLAG_NEW_COIL_FOLDER = False


def check_files_in_coil_folder():  # BobinaActual Folder
    timer_check = threading.Timer(0.5, check_files_in_coil_folder)
    timer_check.start()
    global files, warn_deleted, warn_created, boxes_df, FLAG_ALLOW_NEW_FILE
    global FLAG_NEW_COIL_FOLDER

    # thread_list = []
    new_files = []

    # check existance of folder BobinaActual
    FLAG_PATH_BOBINA_ACTUAL_EXISTS = True if os.path.isdir(PATH_BOBINA_ACTUAL) else False
    # 0- Check existence
    if FLAG_PATH_BOBINA_ACTUAL_EXISTS:

        # 0-1 Creating & cleaning
        if warn_created:
            warn_created = False
            print('*Created: new BobinaActual folder')
            clean_boxes_df()

            # 0-2 sorting
        sorted_files_in_bobina_actual = sorted(os.listdir(PATH_BOBINA_ACTUAL))

        # 0-3 appending .png files to new_files
        for i, file in enumerate(sorted_files_in_bobina_actual):
            if file.endswith('.png') and not file.startswith('_analyzed'):
                new_files.append(file)

        # 0-4 Check if created || deleted files
        FLAG_CREATED_FILES = True if len(new_files) > len(files) else False
        FLAG_DELETED_FILES = True if len(new_files) < len(files) else False

        if FLAG_CREATED_FILES:  # there are created files
            for i in range(len(new_files)):
                if new_files[i] not in files:
                    files.append(new_files[i])
                    img_path = os.path.join(PATH_BOBINA_ACTUAL, new_files[i])
                    print('*File: ', new_files[i], 'CREATED')

                    # Analyze new file in a thread
                    t_analyze = threading.Thread(name='analyze', target=analyze,
                                                 args=(img_path,))  # args kwark of threading.Thread expects an iterable
                    t_analyze.start()

        elif FLAG_DELETED_FILES:  # there are deleted files
            files = new_files

    # 0- check deletion
    else:
        files = []
        if not warn_created:  # if was created
            print('*Deleted: BobinaActual folder')
            warn_created = True

    # 1- get new coil name
    coil_name = get_new_coil_name()

    # 2- detecting new folder (AAAAAAA-BB_CC_DD-EE_FF_GG)
    if FLAG_NEW_COIL_FOLDER:
        FLAG_NEW_COIL_FOLDER = False

        # RENAME temporal analysis folder
        path_last_coil = os.path.join(PATH_SHARED, coil_name + '_analyzed')
        os.rename(PATH_ANALYZED, path_last_coil)

        # search for excel file
        current_coil_path = os.path.join(PATH_SHARED, folder_str)
        current_excel_file = [s for s in os.listdir(current_coil_path) if ".xls" in s]
        FLAG_EXISTS_WI_XLS = True if len(current_excel_file) > 0 else False

        if FLAG_EXISTS_WI_XLS:  # theres a xls file
            current_excel_file = current_excel_file[0]
            current_excel_file_path = os.path.join(current_coil_path, current_excel_file)
            print('*Found excel file (WebInspector): ', current_excel_file, ' in path', current_excel_file_path)
            webinspector_df = pd.read_excel(current_excel_file_path)
            boxes_df = add_position_column(webinspector_df, boxes_df)
        else:
            print('*NO XLS FILE FOUND IN THE LAST COIL FOLDER')
            # WEBINSPECTOR FILE CKECH PENDING!
        # read excel to extract position

        export_data(path_last_coil)

        print('*COMPLETED COIL', coil_name, 'Analysis')

        # Thread download SGL
        print('*Searching for SGL file - COIL:', coil_name)
        DELAY_TO_DOWNLOAD = 0.5
        timer_sgl_download = threading.Timer(DELAY_TO_DOWNLOAD, sgl.download_sgl, args=('TRL', coil_name))
        timer_sgl_download.start()

    FLAG_ALLOW_NEW_FILE = sgl.get_flag_allow_new_file()

    if FLAG_ALLOW_NEW_FILE:  # from sgl
        sgl.set_false_flag_allow_new_file()
        print('FLAG_ALLOW_NEW_FILE', FLAG_ALLOW_NEW_FILE)
        path_new_download = sgl.get_path_new_download()
        sgl_df = pd.read_excel(path_new_download)
        print('\n\nSGL DATAFRAME:\n', sgl_df)

        # get location to save info
        sgl_excel_newpath = os.path.join(PATH_SHARED, str(sgl_df['bobina'][0]) + '_analyzed', 'sgl.xlsx')
        sgl_writer = pd.ExcelWriter(sgl_excel_newpath, engine='xlsxwriter')
        sgl_df.to_excel(sgl_writer,
                        index=False,
                        header=True,
                        columns=sgl_df.columns,
                        sheet_name=str(sgl_df['bobina'][0]))
        sgl_writer.save()
        sgl_writer.close()

        # seguir a partir de aca para sacar los datos de sgl y sumarselos al excel


#      if coil_name
#      print(coil_name)
#    new_coil_name,FLAG_NEW_COIL = get_new_coil_name()


#    if FLAG_NEW_COIL:
#      eval_thresholds(new_coil_name+'_analyzed')

# resetear new_coil_name
# return

# %% reset
def reset():
    global coil_register
    coil_register = []


# %% __main__
if __name__ == "__main__":
    # Folder globals
    folder_df, fl = scan_folders(PATH_SHARED)  # I want the program to start with this set
    folder_list_tmp = folder_df
    columns = ['Date', 'Time', 'Categ', 'Coordinates', 'Relative Area', 'px2 Area', 'cm2 Area', 'Score', 'Image',
               'Position[m]']  # name of columns of the standard dataframe

    #  thread_check = threading.Thread(target=check_files_in_coil_folder , args=() , name='check')
    #  thread_check.start()
    check_files_in_coil_folder()
    # threading.get_ident() \\\ returns a unique name for each thread

    # Existance of new folder
