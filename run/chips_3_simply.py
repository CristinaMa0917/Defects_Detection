import sys
import random
import math
import re
import time
import numpy as np
import cv2
import h5py
import datetime
import argparse
import os
import warnings
import logging
import tensorflow as tf
import keras.backend as K

# # avoid full GPU occupy
#os.environ['CUDA_VISIBLE_DIVICES']='0'
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)
K.set_session(session)

#create logger
logger = logging.getLogger('Chips Detection')
logger.setLevel(logging.DEBUG)

#set argparser
parser = argparse.ArgumentParser('trainning parameters')
parser.add_argument('--path',type=str,default='/mnt/sh_flex_storage/malu/venv/CHIPS_MRCNN',help='root fir of the project')
parser.add_argument('--model_dir',type=str,default='logs_chips3',help='dir to save logs and trained model ie. logs_chips3')
parser.add_argument('--weight_dir',type=str,default=None,help = 'mask_rcnn_coco.h5')
parser.add_argument('--train_path',type=str,default='/mnt/sh_flex_storage/project/xcos_mask/data/trainset.h5')
parser.add_argument('--test_path',type=str,default='/mnt/sh_flex_storage/project/xcos_mask/data/testset.h5')
parser.add_argument('--cuda',type=str,default='0')
parser.add_argument('--epoch',type=int,default=10)
parser.add_argument('--layer',type=str,default='all')
args = parser.parse_args()
logger.info(args)

# Import Mask RCNN
ROOT_DIR = os.path.abspath(args.path)
sys.path.append(ROOT_DIR)  # To find local version of the library
from mrcnn.config import ChipsConfig
from mrcnn import utils
from utils import ChipsDataset
import mrcnn.model_simply as modellib


if __name__ == '__main__':
    # set path
    ROOT_DIR = os.path.abspath(args.path)
    sys.path.append(ROOT_DIR)  # To find local version of the library
    MODEL_DIR = os.path.join(ROOT_DIR, args.model_dir)
    
    #load dataset
    train_set = h5py.File(args.train_path, 'r')
    test_set = h5py.File(args.test_path, 'r')
    train_images = train_set['input']
    test_images = test_set['input']
    train_masks = train_set['output']
    test_masks = test_set['output']
    del train_set
    del test_set
    NUM_TRAIN = train_images.shape[0]  # 224*224
    NUM_TEST = test_images.shape[0]
    
    # prepare dataset on the fly
    dataset_test = ChipsDataset(test_images,test_masks)
    dataset_test.load_chips(NUM_TEST,"test")
    dataset_test.prepare()

    dataset_train = ChipsDataset(train_images,train_masks)
    dataset_train.load_chips(NUM_TRAIN,"train")
    dataset_train.prepare()
    logger.info('dataset prepared')

    # config the training hyper paras
    config = ChipsConfig()
    config.display()

    model = modellib.MaskRCNN(mode="training", config=config, model_dir=MODEL_DIR)
    if args.weight_dir:
        model.load_weights(args.path+args.weight_dir, by_name=True)  # model_path = set_log_dir (no new checkpoint generated)

    use_multiprocessing=False
    warnings.filterwarnings('ignore')

    #start trainning
    logging.info('training started')
    model.train(dataset_train, dataset_test,
                learning_rate=config.LEARNING_RATE,
                epochs=args.epoch,
                layers=args.layer)

#     model_path = os.path.join(MODEL_DIR, "mask_rcnn_chips_1017.h5")
#     model.keras_model.save_weights(model_path)