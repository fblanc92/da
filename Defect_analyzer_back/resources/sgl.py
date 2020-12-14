# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 08:46:01 2020

@author: FBLANC
"""
#%%
import time,os,threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
#%% check_new_file
'''check_new_file: verifyes if file from sgl was downloaded'''
FLAG_ALLOW_NEW_FILE = False #  Fast solution. This flag will be replaced with the returning method of multithreading

def check_new_download(old_downloads,download_id):
  # globals
  global FLAG_ALLOW_NEW_FILE
  path_new_download = ''
  # consts & flags
  TIMEOUT_DOWNLOAD = 15 # download timeout [secs] since EXPORTAR button was pressed
  FLAG_TIMEOUT_DOWNLOAD = False # indicates timeout was reached
  FLAG_NEW_DOWNLOAD = False # indicates new file was downloaded
  INITIAL_TIME = time.time() # actual time
  DOWNLOAD_FOLDER_PATH = os.path.expanduser('~\Downloads')
  
  while not FLAG_TIMEOUT_DOWNLOAD and not FLAG_NEW_DOWNLOAD:
    elapsed_time = time.time() - INITIAL_TIME

    if elapsed_time > TIMEOUT_DOWNLOAD:
      FLAG_TIMEOUT_DOWNLOAD = True
      print('! Download timeout (coil',download_id,')')

    for file in os.listdir(DOWNLOAD_FOLDER_PATH):
      if file.endswith('.xlsx') and file not in old_downloads:
        FLAG_NEW_DOWNLOAD = True
        print('*New file (coil',download_id,')',file)
        path_new_download = os.path.join(DOWNLOAD_FOLDER_PATH,file)
        FLAG_ALLOW_NEW_FILE = True
        break
      
  return path_new_download

#%%
'''download_sgl: downloads info from selected line and slab/coil ID'''

def download_sgl(linea, download_id): # eg; ACERÍA, ########### configurar los argumentos correctamente. 
  TIMEOUT_DRIVER = 20
  driver = webdriver.Chrome()
  global FLAG_ALLOW_NEW_FILE, path_new_download
  if linea == 'TRL':
    print('*SGL:Trying to donwload data (coil',download_id,')')
    driver.minimize_window()
    driver.get('http://10.210.19.103/Template/GetTemplateGeneral?IdLine=1544007&IdTbl=2#')

    try:
      WebDriverWait(driver, TIMEOUT_DRIVER).until(ec.visibility_of_element_located((By.XPATH, "//span[.='Datos']"))).click()
      WebDriverWait(driver, TIMEOUT_DRIVER).until(ec.visibility_of_element_located((By.XPATH, "//span[.='LINEAS']"))).click() 
      WebDriverWait(driver, TIMEOUT_DRIVER).until(ec.visibility_of_element_located((By.XPATH, "//span[.='Tijera Recorte Lateral']"))).click() 
      WebDriverWait(driver, TIMEOUT_DRIVER).until(ec.visibility_of_element_located((By.ID, "bobina"))).click() 
      input_element = WebDriverWait(driver, TIMEOUT_DRIVER).until(ec.visibility_of_element_located((By.ID,"input_char")))
      input_element.clear()
      input_element.send_keys(download_id)
      WebDriverWait(driver,TIMEOUT_DRIVER).until(ec.visibility_of_element_located((By.ID,'actualizar_char'))).click()
    
      # list of old downloads
      old_downloads = os.listdir(os.path.expanduser('~\Downloads'))
      
      # make old-downloads-scan to detect new files from now on
      path_new_download = check_new_download(old_downloads,download_id)
      
      # download from SGL
      input_element = WebDriverWait(driver, TIMEOUT_DRIVER).until(ec.visibility_of_element_located((By.ID, "exportar"))).click()
      
      
    except TimeoutException as ex:
      print('! SGL:Timeout Exception in opening web(coil',download_id,')')
      
  
  elif linea == 'CC':   
    driver.minimize_window()
    driver.get('http://10.210.19.103/Template/GetTemplateGeneral?IdLine=1544007&IdTbl=2#hIdApp=3&hIdSup=101&hIdIzq=13443&hIdSupCkd=10&hUrl=&hSM=false') 
    WebDriverWait(driver, TIMEOUT_DRIVER).until(ec.visibility_of_element_located((By.XPATH, "//span[.='Datos']"))).click()
    WebDriverWait(driver, TIMEOUT_DRIVER).until(ec.visibility_of_element_located((By.XPATH, "//span[.='LINEAS']"))).click() 
    WebDriverWait(driver, TIMEOUT_DRIVER).until(ec.visibility_of_element_located((By.XPATH, "//span[.='ACERÍA']"))).click() 
    WebDriverWait(driver, TIMEOUT_DRIVER).until(ec.visibility_of_element_located((By.XPATH, "//span[.='Coladas Continuas']"))).click() 
    WebDriverWait(driver, TIMEOUT_DRIVER).until(ec.visibility_of_element_located((By.NAME, "selectable_2"))).click() 
    input_element = WebDriverWait(driver, TIMEOUT_DRIVER).until(ec.visibility_of_element_located((By.ID, "input_char")))
    input_element.clear()
    input_element.send_keys(download_id)
    WebDriverWait(driver, TIMEOUT_DRIVER).until(ec.visibility_of_element_located((By.ID, "actualizar_char"))).click() 
    # list of old downloads
    old_downloads = os.listdir(os.path.expanduser('~\Downloads'))
    # download from SGL
    input_element = WebDriverWait(driver, TIMEOUT_DRIVER).until(ec.visibility_of_element_located((By.ID, "exportar"))).click()
    # check if downloaded
    thread_check_new_download = threading.Thread(target = check_new_download, args = (old_downloads,))
    thread_check_new_download.start()
     
  else:
    
    print('* DOWNLOAD ERROR')
  
    
  return
#%% get new download path
def get_flag_allow_new_file():
  global FLAG_ALLOW_NEW_FILE
  return FLAG_ALLOW_NEW_FILE

#get_path_new_download
def get_path_new_download():
  global path_new_download
  return path_new_download

def set_false_flag_allow_new_file():
  global FLAG_ALLOW_NEW_FILE
  FLAG_ALLOW_NEW_FILE = False

#%%
#OFFSET_START_DOWNLOADING = 1 # Two hours to attempt the first download
#
## THREAD download coil info from sgl
#thread_download_sgl = threading.Timer(interval = OFFSET_START_DOWNLOADING , function = download_sgl, args = ('TRL', '249511E'))
#thread_download_sgl.start()
















