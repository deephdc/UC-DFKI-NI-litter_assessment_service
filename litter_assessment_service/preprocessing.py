import os
import numpy as np
import yaml

from keras.models import load_model

def warm(model_name):
    """
    load keras model
    """
    wd = os.getcwd()
    path = os.path.join(wd, model_name)
    model = load_model(path)
    return model

def get_image_tiles(image, tile_size):
    """
    runs image slicer on input image and returns np.ndarray with image tiles.
    """
    shape = image.shape
    tile_size_PLD = 128

    if isinstance(tile_size_PLD, int):
        grid_row_len = shape[0]//tile_size - (shape[0]//tile_size)%2
        grid_col_len = shape[1]//tile_size - (shape[1]//tile_size)%2
    if not isinstance(tile_size_PLD, int):
        grid_row_len = shape[0]//tile_size
        grid_col_len = shape[1]//tile_size

    #array where results get saved
    X = np.zeros((grid_row_len*grid_col_len, tile_size,tile_size,shape[2]))

    for i in range(grid_row_len):
        for j in range(grid_col_len):
            X[i*grid_col_len+j] = image[i*tile_size:(i+1)*tile_size, j*tile_size:(j+1)*tile_size, :]

    X = X.astype('float32')
    X = X[:,:,:,:3]
    X /= 255
    return X, (grid_row_len, grid_col_len)

def load_configs(plot_type):
    """
    returns colors and labels for plot as specified in config.yaml file
    """
    wd = os.getcwd()
    path = os.path.join(wd, 'litter_assessment_service/litter_assessment_service/configs.yaml')
    with open(path, 'rb') as f:
        params = yaml.safe_load(f)
        color = params['plot params'][f'colors {plot_type}']
        label = params['label'][f'label {plot_type}']
    return color, label
