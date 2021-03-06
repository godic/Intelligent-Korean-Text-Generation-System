import numpy as np
import pandas as pd
import util
from CustomLayers import generator


corpus = util.loadCorpus(rm_iname=False)
code2vec = util.loadIcode(val="vec")
char2id = util.loadChar(val="id")
id2char = util.loadChar(val="dict")
dictionary = np.load("../data/dictionary.npy", allow_pickle=True)

print("Load Data")

batch_size = 1000
seq_length = 2
char_size = id2char.shape[0]
corpus_size = corpus.shape[0]
epoch = 10
print("setup some parameter")

corpus_max_len = np.array([])
for i in range(corpus.shape[0] // batch_size):
  top_len = 0
  for j in range(batch_size):
    if top_len < corpus[i * batch_size + j][0].shape[0]:
      top_len = corpus[i * batch_size + j][0].shape[0]
  corpus_max_len = np.append(corpus_max_len, top_len)
print("corpus's max length set: ", corpus_max_len)

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, LSTM, TimeDistributed, Input, concatenate
from tensorflow.keras.optimizers import Adam
from keras import backend as K
from keras.callbacks import ModelCheckpoint
from util import perplexity
K.clear_session()

seq_input = Input(shape=(None, char_size), name="seq_input")
lstm1 = LSTM(256, return_sequences=True)(seq_input)
lstm2 = LSTM(256, return_sequences=True)(lstm1)
lstm3 = LSTM(256, return_sequences=True)(lstm2)

icode_input = Input(shape=(None, 14), name="icode_input")

ann = concatenate([lstm3, icode_input])
ann = TimeDistributed(Dense(char_size, activation='softmax', name="output"))(ann)

model = Model(inputs=[seq_input, icode_input], outputs=[ann])
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy', perplexity])
model.summary()
# model_path = "../data/models/20200908/v3/" + '20200908_{epoch:02d}_{perplexity:.4f}.h5'
# cb_checkpoint = ModelCheckpoint(filepath=model_path, monitor='perplexity', verbose=1, save_best_only=False)
# model.fit(generator(corpus, batch_size, corpus_max_len), steps_per_epoch=corpus_size//batch_size, epochs=epoch, verbose=1, callbacks=[cb_checkpoint])
history = model.fit(generator(corpus, batch_size, corpus_max_len), steps_per_epoch=corpus_size//batch_size, epochs=epoch, verbose=1)
model.save('../data/models/20200915_10_adam_v1.h5') # date_epoch_version
hist_df = pd.DataFrame(history.history)
with open("../data/20200912_20_adam_v2.csv", mode='w') as f:
    hist_df.to_csv(f)

# from keras.models import load_model
# from util import perplexity
# model = load_model('../data/models/20200829_20_v1.h5', custom_objects={'perplexity':perplexity}, compile=False)
# model.summary()

# fw = util.loadFirstWords()
#
# def sentence_generation(model, length):
#     ix = [fw[np.random.randint(fw.shape[0]-2)]]
#     y_char = [id2char[ix[-1]]]
#
#     X = np.zeros((1, length, char_size))
#     Y = np.zeros((1, length, 14))
#
#     Y[0] = np.array(code2vec['Q01A01']) * 10 #한식/백반/한정식
#
#     for i in range(0, length):
#
#         X[0][i][ix[-1]] = 1
#         ix = util.weightedPick(model.predict([X[:, :i+1, :],Y[:, :i+1, :]])[0][-1], 'Q01A01')
#         while ix == char_size - 1:
#             ix = util.weightedPick(model.predict([X[:, :i + 1, :], Y[:, :i + 1, :]])[0][-1], 'Q01A01')
#
#         y_char.append(id2char[ix[-1]])
#
#         if ix == char_size - 2:
#             break
#
#     return ('').join(y_char)
#
# for i in range(10):
#     store_name, first = sentence_generation(model, 10)
#     while util.searchDict(store_name, dictionary, first):
#         store_name, first = sentence_generation(model, 10)
#
#     print(store_name)