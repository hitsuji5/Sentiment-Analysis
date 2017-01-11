from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers.embeddings import Embedding
from keras.preprocessing import sequence
import os
import json
import re
import numpy as np

def LSTM_model(weights_path=None, top_words=5000, embedding_vector_length=32,
         max_review_length=100):
    model = Sequential()
    model.add(Embedding(top_words, embedding_vector_length, input_length=max_review_length))
    model.add(LSTM(100))
    model.add(Dense(1, activation='sigmoid'))
    if weights_path:
        model.load_weights(weights_path)
    return model

class Classifier(object):
    def __init__(self, model, word_index, max_length=100):
        self.model = model
        self.max_length = max_length
        self.word_index = word_index

    def preprocess(self, texts):
        x = []
        for text in texts:
            s = re.sub('<[^>]*>', '', text)
            emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)', s.lower())
            s = re.sub('[\W]+', ' ', s.lower())  + ' '.join(emoticons).replace('-', '')
            x.append([self.word_index.get(token, 1) + 3 for token in s.split()])
        x = sequence.pad_sequences(np.array(x), maxlen=self.max_length)
        return x

    def predict(self, texts):
        x = self.preprocess(texts)
        scores = self.model.predict(x)
        scores = [score[0] for score in scores]
        return scores

cur_dir = os.path.dirname(__file__)
model = LSTM_model(os.path.join(cur_dir, 'classifier', 'model.h5'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
with open(os.path.join(cur_dir, 'classifier', 'word_index.json'), 'r') as f:
    word_index = json.load(f)

clf = Classifier(model, word_index)
