#!/usr/bin/env python
# coding: utf-8

# # Object Detection Demo
# Welcome to the object detection inference walkthrough!  This notebook will walk you step by step through the process of using a pre-trained model to detect objects in an image. Make sure to follow the [installation instructions](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md) before you start.

# # Imports

# In[13]:


import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import cv2
import pandas as pd

from distutils.version import StrictVersion
from collections import defaultdict
from io import StringIO

import tkinter
import matplotlib
#matplotlib.use('tkAgg')

from matplotlib import pyplot as plt
plt.rcParams.update({'figure.max_open_warning':0})
from PIL import Image

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("..")
from object_detection.utils import ops as utils_ops

if StrictVersion(tf.__version__) < StrictVersion('1.12.0'):
  raise ImportError('Please upgrade your TensorFlow installation to v1.12.*.')

#import accesories # automatically starts to run the thread because check function is called on the bottom
# ## Env setup

# In[41]:


# This is needed to display the images.
#%matplotlib inline
#%matplotlib auto
#get_ipython().run_line_magic('matplotlib', 'auto')


# ## Object detection imports
# Here are the imports from the object detection module.

# In[42]:


from object_detection.utils import label_map_util

from object_detection.utils import visualization_utils as vis_util

# # Model preparation 

# ## Variables
# 
# Any model exported using the `export_inference_graph.py` tool can be loaded here simply by changing `PATH_TO_FROZEN_GRAPH` to point to a new .pb file.  
# 
# By default we use an "SSD with Mobilenet" model here. See the [detection model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) for a list of other classes that can be run out-of-the-box with varying speeds and accuracies.

# In[43]:


# What model to download.
#MODEL_NAME = 'defectos_graph'
#MODEL_NAME = 'fb_winsp_graph'
#MODEL_FILE = MODEL_NAME + '.tar.gz'
#DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
#PATH_TO_FROZEN_GRAPH = 'C:/tensorflow/classes/research/object_detection/fb_winsp_graph/frozen_inference_graph.pb'
#PATH_TO_FROZEN_GRAPH = 'C:/tensorflow/classes/research/object_detection/fb_winsp_faster_rcnn_graph/frozen_inference_graph.pb'
#PATH_TO_FROZEN_GRAPH = 'C:/tensorflow/tuto/classes/research/object_detection/graph/frozen_inference_graph.pb'
PATH_TO_FROZEN_GRAPH = 'C:/Users/fblanc.TERNIUM/Desktop/LACA/det_planchones/models/research/object_detection/steel_slab_graph_ssd/frozen_inference_graph.pb'
# List of the strings that is used to add correct label for each box.
#PATH_TO_LABELS = os.path.join('training', 'object-detection.pbtxt')
#PATH_TO_LABELS = os.path.join('data','mscoco_label_map.pbtxt')
PATH_TO_LABELS = r'C:/Users/fblanc.TERNIUM/Desktop/LACA/det_planchones/models/research/object_detection/training/steel_slab_categs.pbtxt'


# ## Download Model

# In[44]:


#opener = urllib.request.URLopener()
#opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
#tar_file = tarfile.open(MODEL_FILE)
#for file in tar_file.getmembers():
#  file_name = os.path.basename(file.name)
#  if 'frozen_inference_graph.pb' in file_name:
#    tar_file.extract(file, os.getcwd())


# ## Load a (frozen) Tensorflow model into memory.

# In[45]:


detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.GraphDef()
  with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')


# ## Loading label map
# Label maps map indices to category names, so that when our convolution network predicts `5`, we know that this corresponds to `airplane`.  Here we use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine

# In[46]:


#CORRECCION DE PATH_TO_LABELS(en original, no en el nuevo modelo)
#PATH_TO_LABELS = 'C:/tensorflow/classes/research/object_detection/data/mscoco_label_map.pbtxt'

category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)


# ## Helper code

# In[47]:


def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)
#def load_image_into_numpy_array(image):
#    return np.asarray(image)  


# # Detection

# In[54]:


# For the sake of simplicity we will use only 2 images:
# image1.jpg
# image2.jpg
# If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
#PATH_TO_TEST_IMAGES_DIR = 'C:/test_images/'
#TEST_IMAGE_PATHS = [ os.path.join(PATH_TO_TEST_IMAGES_DIR, 'img{}.jpg'.format(i)) for i in range(0,3) ]#3-19 20-35
PATH_TO_TEST_IMAGES_DIR = 'C:/test_images_steel_slab'

#cant = len(os.listdir(PATH_TO_TEST_IMAGES_DIR))
#TEST_IMAGE_PATHS = [ os.path.join(PATH_TO_TEST_IMAGES_DIR, 'img{}.jpg'.format(i)) for i in range(cant) ]#3-19 20-35
TEST_IMAGE_PATHS = sorted(os.listdir(PATH_TO_TEST_IMAGES_DIR),key=lambda x: os.path.getctime(os.path.join(PATH_TO_TEST_IMAGES_DIR,x)),reverse=True)
for i,im in enumerate(TEST_IMAGE_PATHS):
    TEST_IMAGE_PATHS[i] = os.path.join(PATH_TO_TEST_IMAGES_DIR , im)
# Size, in inches, of the output images.
IMAGE_SIZE = (12, 8)


# In[55]:


def run_inference_for_single_image(image, graph):
  with graph.as_default():
    with tf.Session() as sess:
      ops = tf.get_default_graph().get_operations()
      all_tensor_names = {output.name for op in ops for output in op.outputs}
      tensor_dict = {}
      for key in [
          'num_detections', 'detection_boxes', 'detection_scores',
          'detection_classes', 'detection_masks'
      ]:
        tensor_name = key + ':0'
        if tensor_name in all_tensor_names:
          tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
              tensor_name)
      if 'detection_masks' in tensor_dict:
        detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
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


# In[56]:
  

for image_path in TEST_IMAGE_PATHS:
    
    image = Image.open(image_path).convert('RGB')
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.

    image_np = load_image_into_numpy_array(image)
    #image_np = cv2.imread(image_path,1)
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    # Actual detection.
    output_dict = run_inference_for_single_image(image_np_expanded, detection_graph)
    # Visualization of the results of a detection.
    
#    print(output_dict['detection_boxes'][])
    #print('\nImage', i+1,' ',image.size[0],'x',image.size[1],' ', image_path)
    
    image_np = vis_util.visualize_boxes_and_labels_on_image_array(
            image_np,
            output_dict['detection_boxes'],
            output_dict['detection_classes'],
            output_dict['detection_scores'],
            category_index,
            instance_masks=output_dict.get('detection_masks'),
            use_normalized_coordinates=True,
            line_thickness=2)
    plt.figure(figsize=IMAGE_SIZE)
    plt.gcf().canvas.set_window_title(image_path)
    plt.imshow(image_np)    
