# -*- coding: utf-8 -*-
"""image_caption.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1NAM5zbDJlEbLMga83Quy5Y7BZ5e_KNbg
"""

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/

!kaggle datasets download -d adityajn105/flickr8k

import zipfile
zip_ref = zipfile.ZipFile('/content/flickr8k.zip', 'r')
zip_ref.extractall('/content')
zip_ref.close()

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.applications import VGG16
from  tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import Model
from tensorflow.keras.utils import plot_model
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.layers import Input, Dense, LSTM, Embedding, Dropout, add
import numpy as np

BASE_DIR = '/content'

model = VGG16()
model = Model(inputs=model.inputs , outputs = model.layers[-2].output)
model.summary()

import os

features = {}
directory = os.path.join(BASE_DIR, 'Images')

for image_name in os.listdir(directory):
   img_path = os.path.join(directory,image_name)
   image = load_img(img_path , target_size=(224,224))
   image = img_to_array(image)
   image = image.reshape((1,image.shape[0],image.shape[1],image.shape[2]))

   image = preprocess_input(image)

   feature_img = model.predict(image)

   image_id = image_name.split('.')[0]
   features[image_id] = feature_img

import pickle

import pickle

with open('features.pkl', 'wb') as f:
  pickle.dump(features, f)

from google.colab import files
files.download('features.pkl')

with open(os.path.join(BASE_DIR, 'features(1).pkl'), 'rb') as f:
    first_bytes = f.read(10)
    print(first_bytes)

with open(os.path.join(BASE_DIR, 'features(1).pkl'), 'rb') as f:
  features = pickle.load(f)

with open(os.join(BASE_DIR, 'captions.txt'), 'r') as f:
  next(f)
  captions_doc = f.read()

mapping_caption = {}

for line in captions_doc.split('\n') :
    token = line.split(',')

    if len(line) < 2:
      continue
    img_id = token[0]
    caption = token[1]

    img_id = img_id.split('.')[0]

    caption = " ".join(caption)

    if img_id not in mapping_caption:
      mapping_caption[img_id] = []

    mapping_caption[img_id].append(caption) ;

def clean(mapping_caption):
  for key,captions in mapping_caption.items():
    for i in range(len(captions)):
      caption = captions[i];
      caption = caption.lower()
      caption = caption.replace('[^A-Za-z]','')
      caption = caption.replace('\s+', ' ')
      caption = '<start> ' + " ".join([word for word in caption.split() if len(word)>1]) + '<end>'

clean(mapping_caption)

all_caption = []

for key in mapping_caption:
   for caption in mapping_caption[key]
     all_caption.append(caption)

tokenizer = Tokenizer()
tokenizer.fit_on_texts(all_caption)
vocab_size = len(tokenizer.word_index) + 1

max_length = max(len(caption.split()) for caption in all_caption)

image_ids = list(mapping_caption.keys())
split = int(len(image_ids) * 0.90)
train = image_ids[:split]
test = image_ids[split:]

def data_generator(data_keys,mapping_caption ,feature_img,tokenizer,max_length,vocab_size,batch_size):

  x1,x2,y = list(),list(),list()

  n = 0

  while True :
    for key in data_keys:
      n= n + 1

      captions = mapping_caption[key]

      for caption in captions:
        seq = tokenizer.texts_to_sequences([caption])[0]

        for i in range(1,len(seq)):

          in_seq , out_seq = seq[:i] , seq[i]

          in_seq = pad_sequences([in_seq],maxlen=max_length)[0]

          out_seq = to_categorical([out_seq],num_classes=vocab_size)[0]

          x1.append(feature_img[key][0])
          x2.append(in_seq)
          y.append(out_seq)

        if n == batch_size:
          x1,x2,y = np.array(x1) , np.array(x2) , np.array(y)
          yield [x1,x2] , y
          x1,x2,y = list(),list(),list()
          n = 0

input1 = Input(shape=(4096,))
fe1 = Dropout(0.4)(input1)
fe2 = Dense(256 , activation='relu')(fe1)

input2 = Input(shape=(max_length,))
se1 = Embedding(vocab_size,256,mask_zero=True)(input2)
se2 = Dropout(0.4)(se1)
se3 = LSTM(256)(se2)

decoder1 = add([fe2 ,se3])
decoder2 = Dense(256 , activation='relu')(decoder1)
outputs = Dense(vocab_size , activation='softmax')(decoder2)

model = Model(inputs=[input1,input2],outputs=outputs)

model.compile(loss='categorical_crossentropy',optimizer='adam')
plot_model(model,show_shapes=True)

epochs = 25
batch_size = 32
steps = len(train) // batch_size

for i in range(epochs):

    generator = data_generator(train,mapping_caption ,feature_img,tokenizer,max_length,vocab_size,batch_size)

    model.fit(generator, epochs=1, steps_per_epoch=steps, verbose=1)

def idx_to_word(integer, tokenizer):
    for word, index in tokenizer.word_index.items():
        if index == integer:
            return word
    return None

def predict_caption(model, image, tokenizer, max_length):

    in_text = '<start>'
    for i in range(max_length):
        sequence = tokenizer.texts_to_sequences([in_text])[0]
        sequence = pad_sequences([sequence], max_length, padding='post')
        yhat = model.predict([image, sequence], verbose=0)
        yhat = np.argmax(yhat)
        word = idx_to_word(yhat, tokenizer)
        if word is None:
            break
        in_text += " " + word
        if word == '<end>':
            break
    return in_text