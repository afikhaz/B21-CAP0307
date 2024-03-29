# -*- coding: utf-8 -*-
"""model_fatigue.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DAZovMvMkG8F0q78eVI3xtmD6Hhv0udc
"""

!pip install split-folders

import splitfolders
import os
import zipfile

local_zip = '/content/dataset.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('/content')
zip_ref.close()


base_dir = '/content/Dataset'
train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'val')

from google.colab import drive
drive.mount('/content/drive')

splitfolders.ratio("/content/dataset",base_dir,ratio=(0.8,0.2))

import tensorflow as tf
from tensorflow.keras.applications import MobileNet
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from matplotlib import pyplot as plt

train_datagen = ImageDataGenerator(
                    rescale=1./255,
                    fill_mode = 'nearest')

train_generator = train_datagen.flow_from_directory(
        train_dir, 
        target_size=(150,150),
        color_mode="rgb",  
        batch_size=10,
        class_mode='binary')

validation_datagen = ImageDataGenerator(
                    rescale=1./255,
                    fill_mode = 'nearest')

validation_generator = train_datagen.flow_from_directory(
        validation_dir, 
        target_size=(150,150),
        color_mode="rgb",  
        batch_size=10,
        class_mode='binary')

baseMobnet = MobileNet(input_shape = (150, 150, 3), # Shape of our images
include_top = False, # Leave out the last fully connected layer
weights = 'imagenet')

baseMobnet.trainable=False

model = tf.keras.Sequential([
                          baseMobnet,
                          tf.keras.layers.Flatten(),  
                          tf.keras.layers.Dense(512, activation='relu'),
                          tf.keras.layers.Dropout(0.2),
                          tf.keras.layers.Dense(6, activation='sigmoid')])

model.summary()

model.compile(optimizer = "RMSprop", loss = 'sparse_categorical_crossentropy',metrics = ['acc'])

hist = model.fit(
      train_generator,
      steps_per_epoch=10, 
      epochs=100,
      validation_data=validation_generator, 
      validation_steps=1,
      verbose=1)

plt.plot(hist.history['acc'])
plt.plot(hist.history['val_acc'])
plt.plot(hist.history['loss'])
plt.plot(hist.history['val_loss'])

plt.title('Ploting akurasi dan loss')

plt.ylabel('Akurasi dan Loss')
plt.xlabel('epoch')

plt.legend(['train_Acc', 'val_Acc','train_Loss', 'val_Loss'])
plt.show()

# Commented out IPython magic to ensure Python compatibility.

import numpy as np
from google.colab import files
from keras.preprocessing import image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
# %matplotlib inline

uploaded = files.upload()

for fn in uploaded.keys():

  path = fn
  img = image.load_img(path, target_size=(150,150,3),color_mode="rgb")
  imgplot = plt.imshow(img)
  x = image.img_to_array(img)
  x = x / 255
  x = np.expand_dims(x, axis=0)

  images = np.vstack([x])
  classes = model.predict(images, batch_size=10)

  print(classes)

export_dir = 'saved_model/1'

tf.saved_model.save(model,export_dir=export_dir)

optimization = tf.lite.Optimize.OPTIMIZE_FOR_SIZE
converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)

converter.optimizations = [optimization]
tflite_model = converter.convert()

import pathlib
tflite_model_file = pathlib.Path('./model.tflite')
tflite_model_file.write_bytes(tflite_model)