import os
import yaml
import numpy as np
def load_config(name:str):
    with open(os.path.join('cfg', name), 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
    camera_matrix:list = config['camera_matrix']['data']
    camera_matrix = np.array(camera_matrix, dtype=np.double).reshape(3,3)
    dist_coeffs:list = config['distortion_coefficients']['data']
    dist_coeffs = np.array(dist_coeffs, dtype=np.double)
    return camera_matrix, dist_coeffs
