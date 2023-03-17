# Mushroom classification

## Prerequisites
- conda
- NVIDIA GPU

## Environment setup

Run the following in the project root directory to set up conda environment:
```bash
$ conda create -n mc python=3.8
$ conda activate mc
$ export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/ # or mkdir -p $CONDA_PREFIX/etc/conda/activate.d; echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/' > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
$ python3 -m pip install tensorflow
$ pip install -r requirements.txt
```

## Usage

Unpack `prepared.zip` and run the following to start training the classifier:
```bash
$ python3 train.py
```
