# -*- coding: utf-8 -*-
"""layer1-canidae-CustomLayer

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1C7U88Hdlx8QplERyvFSsRXvBKuuLj3VK
"""

import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import matplotlib
matplotlib.use("Agg")

import keras
from keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
from keras.layers import Dense, Flatten, LocallyConnected1D, LocallyConnected2D, Reshape, Concatenate, Lambda
from keras import optimizers
from keras.models import Sequential, Model
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras import backend as K
from keras.layers import Layer

import numpy as np
import pandas as pd
import h5py

import random
import math

from custom_generator import create_good_generator

#Magic numbers
num_epochs = 100
bs = 64
img_rows = 224
img_cols = 224
flatten_shape = 1000

# Forked from Ken's codes

imagenet_train = '/mnt/fast-data17/datasets/ILSVRC/2012/clsloc/train/'
ImageGen = ImageDataGenerator(fill_mode='nearest',
                              horizontal_flip=True,
                              rescale=None,
                              preprocessing_function=preprocess_input,
                              data_format="channels_last",
                              validation_split=0.1
                              )
df_classes = pd.read_csv('groupings-csv/canidae_Imagenet.csv', usecols=['wnid'])
classes = sorted([i for i in df_classes['wnid']])

good_train_generator, steps = create_good_generator(ImageGen, 
                                                    imagenet_train,
                                                    batch_size=bs, 
                                                    target_size = (img_rows, img_cols), 
                                                    class_mode='sparse', 
                                                    subset= 'training', 
                                                    classes=classes)

good_validation_generator, steps_val = create_good_generator(ImageGen, 
                                                    imagenet_train,
                                                    batch_size=bs, 
                                                    target_size = (img_rows, img_cols), 
                                                    class_mode='sparse', 
                                                    subset= 'validation', 
                                                    classes=classes)

#Customize a constraint class that clip w to be [K.epsilon(), inf]
from keras.constraints import Constraint

class CustomConstraint (Constraint):
  
    def __call__(self, w):      
        new_w = K.clip(w, K.epsilon(), None)
        return new_w

#Customize a element-wise multiplication layer with trainable weights
class SinglyConnected(Layer):
    def __init__(self,
                 kernel_constraint=None,
                 **kwargs):
        self.kernel_constraint = kernel_constraint
        super(SinglyConnected, self).__init__(**kwargs)

    def build(self, input_shape):
        if input_shape[-1] is None:
            raise ValueError('Axis ' +  + ' of '
                             'input tensor should have a defined dimension '
                             'but the layer received an input with shape ' +
                             str(input_shape) + '.')
        #self.input_spec = InputSpec(ndim=len(input_shape),
         #                           axes=dict(list(enumerate(input_shape[1:], start=1))))
        
        self.kernel = self.add_weight(name='kernel', 
                                      shape=input_shape[1:],
                                      initializer='uniform',
                                      constraint=self.kernel_constraint,
                                      trainable=True)
        super(SinglyConnected, self).build(input_shape)  # Be sure to call this at the end

    def call(self, x):
        return np.multiply(x,self.kernel)

    def compute_output_shape(self, input_shape):
        return (input_shape)

#Build the model
vgg16_model = VGG16(weights = 'imagenet', include_top=True, input_shape = (img_rows, img_cols, 3))

for layer in vgg16_model.layers:
    layer.trainable = False
    
last = vgg16_model.layers[-2].output
x = SinglyConnected(kernel_constraint= CustomConstraint())(last)
preds = vgg16_model.layers[-1](x)
for layer in vgg16_model.layers[-1:]:
  x = layer(x)

model = Model(vgg16_model.input, x)

model.compile(loss='categorical_crossentropy', 
              optimizer='adam', 
              metrics=['accuracy'])

model.summary()

#Callbacks
callbacks = [EarlyStopping(monitor='val_loss', patience=2, verbose = 1),
             ModelCheckpoint(filepath='layer1-canidae-model-CustomLayer.h5', monitor='val_loss', save_best_only=True)]

model.fit_generator(
        train_generator,
        steps_per_epoch=steps,
        epochs=num_epochs,
        callbacks = callbacks, 
        validation_data=validation_generator, 
        validation_steps=steps_val)
