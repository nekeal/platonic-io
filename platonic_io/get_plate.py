from os.path import splitext
from typing import Union

import cv2
import numpy as np

from platonic_io import logger

from .local_utils import detect_lp


def load_model(path):
    from keras.models import model_from_json  # long running import

    try:
        path = splitext(path)[0]
        with open("%s.json" % path, "r") as json_file:
            model_json = json_file.read()
        model = model_from_json(model_json, custom_objects={})
        model.load_weights("%s.h5" % path)
        logger.debug("Loading model successfully...")
        return model
    except Exception:
        logger.exception("Unhandled exception occured duing model loading")


def preprocess_image(image, resize=False):
    """
    scale from [0 255] to [0 1] and switch BGR to RGB
    """
    img = image
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img / 255
    if resize:
        img = cv2.resize(img, (224, 224))
    return img


def get_plate(image_path, wpod_net, d_max=608, d_min=256):
    vehicle = preprocess_image(image_path)
    ratio = float(max(vehicle.shape[:2])) / min(vehicle.shape[:2])
    side = int(ratio * d_min)
    bound_dim = min(side, d_max)
    _, lp_img, _, cor = detect_lp(wpod_net, vehicle, bound_dim, lp_threshold=0.5)
    return lp_img, cor


def draw_box(image, coordinates, thickness=3):
    vehicle_image = image
    for c in coordinates:
        pts_list = []
        x_coordinates = c[0]
        y_coordinates = c[1]
        # store the top-left, top-right, bottom-left, bottom-right
        # of the plate license respectively
        for i in range(4):
            pts_list.append([int(x_coordinates[i]), int(y_coordinates[i])])

        pts: np.array = np.array(pts_list, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(vehicle_image, [pts], True, (0, 255, 0), thickness)
    return vehicle_image


def get_width_height_ratio(cor):
    x_coordinates = cor[0]
    y_coordinates = cor[1]
    # store the top-left, top-right, bottom-left, bottom-right
    # of the plate license respectively
    pts = []
    for i in range(4):
        pts.append([int(x_coordinates[i]), int(y_coordinates[i])])
    width = abs(pts[1][0] - pts[0][0])
    height: Union[int, float] = abs(pts[0][1] - pts[2][1])
    if height == 0:
        height = 0.001
    return width / height


def sort_contours(contours, reverse=False):
    """
    sort given contours from left to right
    """
    key = 0
    bounding_boxes = [cv2.boundingRect(c) for c in contours]
    (contours, bounding_boxes) = zip(
        *sorted(zip(contours, bounding_boxes), key=lambda b: b[1][key], reverse=reverse)
    )
    return contours


# pre-processing input images and pedict with model
def predict_from_model(image, model, labels):
    image = cv2.resize(image, (80, 80))
    image = np.stack((image,) * 3, axis=-1)
    prediction = labels.inverse_transform(
        [np.argmax(model.predict(image[np.newaxis, :]))]
    )
    return prediction
