"""
Image Annotator

by Amir Kardoost and Beatriz Fernansdes
"""

import os
import pandas as pd
import czifile
import numpy as np
import tifffile
import nibabel as nib
from PyQt5.QtWidgets import QSlider
from PyQt5.QtGui import QPainter, QPen, QFontMetrics
from PyQt5.QtCore import Qt, QRectF
from scipy import ndimage


def iou(box1, box2):
    """Compute IoU of two bounding boxes."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    intersection_area = max(0, x2 - x1) * max(0, y2 - y1)
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - intersection_area
    if union_area > 1:
        result = intersection_area / union_area
    else:
        result = 1.0
    return result


def non_maximum_suppression(boxes, iou_threshold):
    """
    Apply Non-Maximum Suppression (NMS) to suppress overlapping
    bounding boxes."""
    if len(boxes) == 0:
        return []
    selected_boxes = []
    while boxes:
        current_box = boxes.pop(0)
        selected_boxes.append(current_box)
        boxes = [box for box in boxes
                 if iou(current_box, box) <= iou_threshold]
    return selected_boxes


def list_directories(folder_path):
    """Lists all directories within a given folder."""
    # Make sure the folder_path is a directory
    if not os.path.isdir(folder_path):
        return f"{folder_path} is not a valid directory."

    # List all entries in the folder
    entries = os.listdir(folder_path)

    # Filter out directories from all entries
    directories = [entry for entry in entries if
                   os.path.isdir(os.path.join(folder_path, entry))]

    return directories


def read_csv_files(csv_files_path):
    """Read all the available CSV files in the results folder."""
    directories = list_directories(csv_files_path)
    print(directories)
    all_data = {}
    for entry in directories:
        csv_path = os.path.join(csv_files_path, entry,
                                'detected_regions_on_all_images.csv')
        print(os.path.abspath(csv_path))
        df = pd.read_csv(csv_path)
        all_data[entry] = df.copy()
    return all_data


def filter_csv_data(image_path, csv_data, models, instance:int = -1):
    "Filter the CSV file based on the File Name"

    raw_name = image_path.split('.')[0]

    filtered_csv_data_for_all_models = {}
    for entry in models:
        filename = os.path.basename(raw_name)
        if entry in csv_data.keys():
            csv_data_for_model = csv_data[entry]
            filtered_csv_data = csv_data_for_model[
                csv_data_for_model['File Name'] == filename]
            if instance == -1:
                filtered_csv_data_for_all_models[entry] = filtered_csv_data[filtered_csv_data['Area'] > 0]
            else:
                filtered_csv_data_for_all_models[entry] = filtered_csv_data[filtered_csv_data['Segmentation Number'] == instance]
    return filtered_csv_data_for_all_models


def get_czi(directory, image_type):
    "Load the raw CZI file"
    message = None
    czi_file = czifile.imread(directory)
    czi_file = np.squeeze(czi_file)

    if image_type == 'Macrophage':
        if len(czi_file.shape) != 4:
            message = "<b>The image must have shape of " + \
                      "[X, Y, Markers, Z-Stack Layers]!</b>" + \
                      "\n<b>Please Select the Image Type ...</b>"
        else:
            czi_file = np.transpose(czi_file, (2, 3, 1, 0))
            assert (len(czi_file.shape) == 4)
            czi_file = czi_file.astype(float)
            for marker in range(czi_file.shape[3]):
                temp_mask = czi_file[:, :, :, marker]
                temp_mask /= temp_mask.max()
                czi_file[:, :, :, marker] = temp_mask*255
    elif image_type == 'Neural':
        if len(czi_file.shape) != 3:
            message = "<b>The image must have shape of [X, Y, Markers]!</b> \n"
            message += "<b>Please Select the Image Type ...</b>"
        else:
            czi_file = np.transpose(czi_file, (1, 2, 0))
            assert (len(czi_file.shape) == 3)
            czi_file = czi_file.astype(float)
            for marker in range(czi_file.shape[2]):
                temp_mask = czi_file[:, :, marker]
                temp_mask /= temp_mask.max()
                czi_file[:, :, marker] = temp_mask*255

    return czi_file, message

def get_tif(directory,):
    "Load the raw TIF file"
    message = None
    tif_file = tifffile.imread(directory)
    tif_file = np.squeeze(tif_file)

    if len(tif_file.shape) != 4:
        message = "<b>The image must have shape of " + \
                    "[Markers, Z-Stack Layers, X, Y]!</b>" + \
                    "\n<b>Please Select the Image Type ...</b>"
    else:
        tif_file = np.transpose(tif_file, (2, 3, 0, 1))
        # print(tif_file.shape)
        assert (len(tif_file.shape) == 4)
        tif_file = tif_file.astype(float)
        tif_file = ndimage.zoom(tif_file, (0.5, 0.5, 1, 1), order=1)
        for marker in range(tif_file.shape[3]):
            temp_mask = tif_file[:, :, :, marker]
            temp_mask /= temp_mask.max()
            tif_file[:, :, :, marker] = temp_mask*255

    return tif_file, message

def get_nibabel(directory):
    "Load the raw NIB file"
    message = None
    nib_file = nib.load(directory)
    nib_file = np.squeeze(nib_file.get_fdata())

    # print(nib_file.shape)

    if len(nib_file.shape) != 4:
        message = "<b>The image must have shape of " + \
                    "[Z-Stack Layers, Markers, X, Y]!</b>" + \
                    "\n<b>Please Select the Image Type ...</b>"
    else:
        nib_file = np.transpose(nib_file, (1, 0, 2, 3))
        # print(nib_file.shape)
        assert (len(nib_file.shape) == 4)
        nib_file = nib_file.astype(float)
        for marker in range(nib_file.shape[3]):
            temp_mask = nib_file[:, :, :, marker]
            temp_mask /= temp_mask.max()
            nib_file[:, :, :, marker] = temp_mask*255

    return nib_file, message