import cv2
import math
from pathlib import Path
from tqdm import tqdm
import pandas as pd


def resize_img(img):
    new_size = 224
    h, w = img.shape[:2]
    scale = max(h / new_size, w / new_size)
    dim = (int(w / scale), int(h / scale))
    horiz_board = (new_size - dim[0]) / 2
    horiz_board = [math.floor(horiz_board), math.ceil(horiz_board)]
    vertic_board = (new_size - dim[1]) / 2
    vertic_board = [math.floor(vertic_board), math.ceil(vertic_board)]

    res = cv2.resize(img, dim)
    res = cv2.copyMakeBorder(
        res,
        vertic_board[0],
        vertic_board[1],
        horiz_board[0],
        horiz_board[1],
        cv2.BORDER_CONSTANT,
        value=0,
    )

    return res


def correct_filenames(raw_dir, conv_filenames):
    raw_dir = Path(raw_dir)

    corrected_num = 0
    for f in raw_dir.glob("*"):
        if f.is_dir():
            correct_filenames(f, conv_filenames)
            continue

        # if f.stem in conv_filenames:
        #     continue

        # forbidden characters: =, +, :
        characters = ["=", "+", ":"]
        for ch in characters:
            correct_filename = f.name.replace(ch, "")
        if correct_filename != f.name:
            correct_path = f.parent / correct_filename
            f = f.rename(correct_path)

            corrected_num += 1

    return corrected_num


def resize_dir_imgs(raw_dir, prep_dir, conv_filenames):
    new_conv_num = 0
    new_filenames = []
    for f in raw_dir.glob("*"):
        if f.stem in conv_filenames:
            continue

        # TODO: rename intial file
        # forbidden characters: =, +, :
        characters = ["=", "+", ":"]
        for ch in characters:
            correct_filename = f.name.replace(ch, "")
        if correct_filename != f.name:
            correct_path = f.parent / correct_filename
            f = f.rename(correct_path)

        img = cv2.imread(str(f), cv2.IMREAD_UNCHANGED)
        changed = resize_img(img)
        cv2.imwrite(str(prep_dir / (f.stem + ".png")), changed)

        new_conv_num += 1
        new_filenames.append(f.stem)
    return new_conv_num, new_filenames


# def prepare_imgs(glob_raw_dir, glob_prep_dir, species):
#     glob_raw_dir = Path(glob_raw_dir)
#     glob_prep_dir = Path(glob_prep_dir)

#     glob_prep_dir.mkdir(exist_ok=True)

#     for s in species:
#         s_raw_dir = glob_raw_dir / s
#         s_prep_dir = glob_prep_dir / s

#         for t in ['downside', 'exist']:
#             prep_dir = s_prep_dir / t

#             prep_dir.mkdir(exist_ok=True, parents=True)
#             resize_dir_imgs(s_raw_dir / t, prep_dir)


def prepare_imgs(glob_raw_dir, glob_prep_dir, metadata_path):
    glob_raw_dir = Path(glob_raw_dir)
    glob_prep_dir = Path(glob_prep_dir)
    metadata_path = Path(metadata_path)

    if metadata_path.exists():
        metadata = pd.read_csv(metadata_path)
    else:
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata = pd.DataFrame(columns=["filename"])
    conv_filenames = set(metadata["filename"])

    glob_prep_dir.mkdir(exist_ok=True)

    correct_filenames(glob_raw_dir, conv_filenames)

    tot_conv_num = 0
    conv_imgs_limit = 90000
    tot_new_filenames = []
    for raw_dir in tqdm(sorted(list(glob_raw_dir.glob("*")))):
        if tot_conv_num > conv_imgs_limit:
            break

        prep_dir = glob_prep_dir  # / raw_dir.name

        prep_dir.mkdir(exist_ok=True)
        new_conv_num, new_filenames = resize_dir_imgs(raw_dir, prep_dir, conv_filenames)

        tot_conv_num += new_conv_num
        tot_new_filenames = tot_new_filenames + new_filenames

    new_metadata = pd.DataFrame({"filename": tot_new_filenames})
    metadata = pd.concat([metadata, new_metadata]).reset_index(drop=True)

    metadata.to_csv(metadata_path, index=False)

    print(f"Converted images: {tot_conv_num}")


def create_unlabeled_split_csv(data_dir, split_path):
    data_dir = Path(data_dir)
    split_path = Path(split_path)

    paths = []
    for f_path in sorted(list(data_dir.glob("*"))):
        f_path = str(Path(f_path.parent.name) / f_path.name)
        paths.append(f_path)
    metadata = pd.DataFrame({"path": pd.Series(paths)})

    print(metadata.head())
    print(metadata.shape[0])

    metadata.to_csv(split_path, index=False)


glob_raw_dir = "data/fungi_train_val/images"
glob_prep_dir = "data/unlabeled/challenge2018/images"
conv_path = "data/metadata/challenge2018.csv"
split_path = "data/unlabeled/challenge2018/split.csv"
# species = ['agaricus_xanthodermus', 'amanita_muscaria', 'amanita_phalloides']
# prepare_imgs(glob_raw_dir, glob_prep_dir, conv_path)  # , species)
create_unlabeled_split_csv(glob_prep_dir, split_path)
# corrected_num = correct_filenames(glob_prep_dir, None)
# print(corrected_num)
