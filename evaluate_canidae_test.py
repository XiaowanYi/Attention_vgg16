# -*- coding: utf-8 -*-
"""evaluate_canidae_test.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1j48AbOrAacir1wRHiTd5H0o9y_v_H80m
"""

import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import matplotlib
matplotlib.use("Agg")

import keras
from keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from keras.layers import Dense, Flatten, LocallyConnected1D, Reshape
from keras import optimizers
from keras.models import Sequential, Model
from keras import backend as K
from keras.models import load_model


import numpy as np
import pandas as pd

bs = 64
img_rows = 224
img_cols = 224

model_file = 'canidae/'
model1_name = os.listdir(model_file)[0]
print ('using model: ' + model_file+model1_name)
model = load_model(model_file+model1_name)



imagenet_test = '/mnt/fast-data16/datasets/ILSVRC/2012/clsloc/val/'
ImageGen = ImageDataGenerator(fill_mode='nearest',
                              horizontal_flip=True,
                              rescale=None,
                              preprocessing_function=preprocess_input,
                              data_format="channels_last",
                              use_multiprocessing=False
                              )

df_classes = pd.read_csv('groupings-csv/canidae_Imagenet.csv', usecols=['wnid'])
classes = sorted([i for i in df_classes['wnid']])

good_train_generator, steps = create_good_generator(ImageGen,
                                                    imagenet_test,
                                                    batch_size=bs,
                                                    target_size = (img_rows, img_cols),
                                                    class_mode='sparse',
                                                    AlextNetAug=False, 
                                                    classes=classes)

in_context_acc = model.evaluate_generator(good_train_generator, steps, verbose=1)

print(in_context_acc)