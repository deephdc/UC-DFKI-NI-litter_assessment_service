# -*- coding: utf-8 -*-
"""
Functions to integrate your model with the DEEPaaS API.
It's usually good practice to keep this file minimal, only performing the interfacing
tasks. In this way you don't mix your true code with DEEPaaS code and everything is
more modular. That is, if you need to write the predict() function in api.py, you
would import your true predict function and call it from here (with some processing /
postprocessing in between if needed).
For example:

    import mycustomfile

    def predict(**kwargs):
        args = preprocess(kwargs)
        resp = mycustomfile.predict(args)
        resp = postprocess(resp)
        return resp

To start populating this file, take a look at the docs [1] and at a canonical exemplar
module [2].

[1]: https://docs.deep-hybrid-datacloud.eu/
[2]: https://github.com/deephdc/demo_app
"""
import tempfile
import os
import logging
import io
import subprocess
import shutil
from zipfile import ZipFile
from pathlib import Path
from PIL import Image

import pkg_resources
import numpy as np

from litter_assessment_service.misc import _catch_error
from litter_assessment_service.plotting import ResultPlot
from litter_assessment_service import fields, classification, preprocessing

BASE_DIR = Path(__file__).resolve().parents[1]

logger = logging.getLogger('__name__')

PLD_model=None
PLQ_model=None

@_catch_error
def get_metadata():
    """
    DO NOT REMOVE - All modules should have a get_metadata() function
    with appropriate keys.
    """
    distros = list(pkg_resources.find_distributions(str(BASE_DIR), only=True))
    if len(distros) == 0:
        raise Exception("No package found.")
    pkg = distros[0]  # if several select first

    meta_fields = {
        "name": None,
        "version": None,
        "summary": None,
        "home-page": None,
        "author": None,
        "author-email": None,
        "license": None,
    }
    meta = {}
    for line in pkg.get_metadata_lines("PKG-INFO"):
        line_low = line.lower()  # to avoid inconsistency due to letter cases
        for k in meta_fields:
            if line_low.startswith(k + ":"):
                _, value = line.split(": ", 1)
                meta[k] = value

    return meta

def get_predict_args():
    """Return the arguments that are needed to perform a  prediciton.

    Returns:
        Dictionary of webargs fields.
      """
    predict_args=fields.PredictArgsSchema().fields
    logger.debug("Web arguments: %d", predict_args)

    return predict_args

def get_train_args(**kwargs):
    return {}

def get_input_data(data):
    """
    Check content type of uploaded data and return list 
    with image names and paths to the stored files
    """
    if data.content_type == 'application/zip':
        tmp_input = tempfile.mkdtemp()
        with ZipFile(data.filename, 'r') as zip_file:
            zip_file.extractall(tmp_input)
        image_names = os.listdir(tmp_input)
        image_file = [os.path.join(tmp_input, image_names[i]) for i in range(len(image_names))]
    else:
        image_file = [data.filename]
        image_names = [data.original_filename]

    return image_names, image_file

def mount_nextcloud(frompath, topath):
    """
    Mount a NextCloud folder in your local machine or viceversa.
    """
    command = ["rclone", "copy", frompath, topath]
    result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = result.communicate()
    return output, error

def warm():
    """
    Load the models for detection and quantification before requests to the API are made
    """
    global model_PLD, model_PLQ
    model_name_PLD = "litter_assessment_service/models/PLD_CNN.h5"
    model_name_PLQ = "litter_assessment_service/models/PLQ_CNN.h5"
    model_PLD = preprocessing.warm(model_name_PLD)
    model_PLQ = preprocessing.warm(model_name_PLQ)

def get_arr_from_bin(image_file):
    """
    Convert path to image_file to np.array
    """
    image=open(image_file,'rb')
    image_file=image.read()
    image_or= Image.open(io.BytesIO(image_file))
    return np.array(image_or).astype(np.uint8)

def save_plot_nextcloud(**kwargs):
    """
    Plot classification results and upload the resulting .jpg file to mounted external storage
    """
    fig = ResultPlot(kwargs['results'], kwargs['type']).get_plot()
    fig.savefig(f'{kwargs["output_path"]}_{kwargs["type"]}.jpg')
    mount_nextcloud(f'{kwargs["output_path"]}_{kwargs["type"]}.jpg', f'{kwargs["to_path"]}')

def return_plot(**kwargs):
    fig = ResultPlot(kwargs['results'], kwargs['type']).get_plot()
    fig.savefig(f'{kwargs["output_path"]}_{kwargs["type"]}.jpg')


@_catch_error
def predict(**kwargs):
    """
    Run inference on uploaded image(s) and run "save_plot(**kwargs)" 
    for the resulting classifications
    """
    data = kwargs["files"]
    image_names, image_files = get_input_data(data)
    to_path='rshare:iMagine_UC1/results'

    tmp_dir = tempfile.mkdtemp()

    #with tempfile.TemporaryDirectory() as tmp_dir:
    for name, file in zip(image_names, image_files):
        output_path=os.path.join(tmp_dir, name[:-4])
        if data.content_type=='application/octet-stream':
            image=get_arr_from_bin(file)
        else:
            image_or = Image.open(file)
            image = np.array(image_or)
        results_PLD = classification.PLD_result(image, image_names, model_PLD)

        if kwargs["PLD_plot"] and kwargs["PLQ_plot"]:
            return_plot(results=results_PLD, type='PLD', output_path=output_path)
            results_PLQ = classification.PLQ_result(results_PLD.c_matrix, image, image_names, model_PLQ)
            return_plot(results=results_PLQ, type='PLQ',output_path=output_path)
            if kwargs["output_type"]=='Download':
                shutil.make_archive(tmp_dir, format = 'zip', root_dir = tmp_dir)
                zip_path = tmp_dir + '.zip'
                return open(zip_path, 'rb')
            
            elif kwargs["output_type"]=='nextcloud':
                save_plot_nextcloud(results=results_PLD, type='PLD', output_path=output_path,to_path=to_path)
                save_plot_nextcloud(results=results_PLQ, type='PLQ', output_path=output_path,to_path=to_path)
            else:
                print(f'no output type selected')

        elif kwargs["PLD_plot"]:
            print(f'starting PLD again')
            return_plot(results=results_PLD, type='PLD', output_path=output_path)
            plot_path=f'{output_path}_PLD.jpg'
            if kwargs["output_type"]=='Download':
                return open(plot_path, 'rb')
            elif kwargs["output_type"]=='nextcloud':
                save_plot_nextcloud(results=results_PLD, type='PLD', output_path=output_path,to_path=to_path)
            else:
                print(f'no output type selected')

        elif kwargs["PLQ_plot"]:
            print(f'starting PLQ again')
            results_PLQ = classification.PLQ_result(results_PLD.c_matrix, image, image_names, model_PLQ)
            return_plot(results=results_PLQ, type='PLQ',output_path=output_path)
            plot_path=f'{output_path}_PLQ.jpg'
            if kwargs["output_type"]=='Download':
                return open(plot_path, 'rb')
            elif kwargs["output_type"]=='nextcloud':
                save_plot_nextcloud(results=results_PLQ, type='PLQ', output_path=output_path,to_path=to_path)
            else:
                print(f'no output type selected')
