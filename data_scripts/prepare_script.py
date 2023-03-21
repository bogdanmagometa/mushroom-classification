import cv2
import math
import os

DATA_FOLDER = 'data/'


def resize_img(img):
    new_size = 300
    h, w = img.shape[:2]
    scale = max(h/new_size, w/new_size)
    dim = (int(w/scale), int(h/scale))
    horiz_board = (new_size - dim[0])/2
    horiz_board = [math.floor(horiz_board), math.ceil(horiz_board)]
    vertic_board = (new_size - dim[1])/2
    vertic_board = [math.floor(vertic_board), math.ceil(vertic_board)]

    res = cv2.resize(img, dim)
    res = cv2.copyMakeBorder(
        res, vertic_board[0], vertic_board[1], horiz_board[0], horiz_board[1], cv2.BORDER_CONSTANT, value=0)

    return res


def augmentate_img():
    pass


def prepare_imgs():
    raw_dir = os.path.join(DATA_FOLDER, 'raw')
    prep_dir = os.path.join(DATA_FOLDER, 'prepared')

    if not os.path.exists(prep_dir):
        os.mkdir(prep_dir)

    for dn in os.listdir(raw_dir):
        dpath = os.path.join(raw_dir, dn)
        prep_subdir = os.path.join(prep_dir, dn)
        if not os.path.exists(prep_subdir):
            os.mkdir(prep_subdir)
        for fn in os.listdir(dpath):
            fpath = os.path.join(dpath, fn)
            if not os.path.isfile(fpath):
                continue
            img = cv2.imread(fpath, cv2.IMREAD_UNCHANGED)
            changed = resize_img(img)
            prep_fpath = os.path.join(prep_subdir, fn)
            cv2.imwrite(prep_fpath, changed)


prepare_imgs()
