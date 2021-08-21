import datetime as dt
from collections import deque
from typing import Type

import numpy as np
import pandas as pd
from ..data_processor import DataProcessor
from ..preprocessed_data import PreprocessedData
from ..raw_data import RawDataSource
from tensorflow import keras


class KerasPreprocessedData(PreprocessedData):
    def __init__(self, ticker: str, data_processor: Type[DataProcessor], raw_data_source: Type[RawDataSource],
                 seq_len: int, batch_size: int, step: int, future_predict_period: str) -> None:
        # validate_ticker(ticker)
        self.data_processor = data_processor(ticker, raw_data_source, seq_len, step, future_predict_period)
        self.seq_len = seq_len
        self.batch_size = batch_size
        self.step = step

    def get_preprocessed_datasets(self):
        (train_x, train_y), (val_x, val_y),  (test_x, test_y) = self.data_processor.get_preprocessed_dfs()

        dataset_train = self.get_dataset_from_df(train_x, train_y)
        dataset_val = self.get_dataset_from_df(val_x, val_y)
        dataset_test = self.get_dataset_from_df(test_x, test_y)

        return dataset_train, dataset_val, dataset_test

    def get_dataset_from_df(self, x: pd.DataFrame, y: pd.DataFrame):

        t = []
        for i in range(self.seq_len-1, len(y), self.seq_len):
            t.append(y[i])

        dataset = keras.preprocessing.timeseries_dataset_from_array(
            x, t,
            sequence_length=self.seq_len,
            sampling_rate=self.step,
            batch_size=self.batch_size,
        )
        return dataset

        #     print(i, ((self.seq_len-1) + self.seq_len*3))
        #     if (i % ((self.seq_len-1) + self.seq_len*3) == 0):
        #         print(i)
        #         print(x[i: i+10])
        #     print(y[i])
        #     print()

        # print()
        # print('Y')
        # print(y[self.seq_len-1: self.seq_len*5])
        # print()

        # sequential_data = []
        # prev_days = deque(maxlen=self.seq_len)
        # # print(x[self.seq_len-1:])
        # print()
        # print('T: ')
        # print(t)
        # print()

        # j = 0
        # for i in x.values:
        #     prev_days.append([n for n in i])
        #     if len(prev_days) == self.seq_len and j < len(t):
        #         sequential_data.append([np.array(prev_days), t[j]])
        #         j += 1

        # X = []
        # y = []

        # for seq, target in sequential_data:  # going over our new sequential data
        #     X.append(seq)  # X is the sequences
        #     y.append(target)  # y is the targets/labels (buys vs sell/notbuy)

        # print()
        # print('SENTDEX')
        # print()
        # for i in range(3):
        #     print(X[i][0], y[i])

        # print()
        # print()
        # print()

        # print()
        # print('KERAS')
        # print()
        # # return np.array(X), y
        # # random.shuffle(sequential_data)

        # print('##############################################')
        # print(len(x), len(y), len(y)//self.seq_len, len(x)/self.seq_len//batch_size)
        # i = 0
        # for x, y in dataset:
        #     i += 1
        # print(i)
        # print('y', len(y))
        # # print('y', y)
        # # print('x', x)
        # #     for i in range(1):
        # #         print('x', x[i][0])
        # print('##############################################')

    def get_preprocessed_prediction_dataset(self, pred_date: dt.date):

        x = self.data_processor.get_preprocessed_prediction_df(pred_date)
        return np.expand_dims(x, 0)

        # To be used when model.predict() is used
        # dataset = keras.preprocessing.timeseries_dataset_from_array(
        #     x,
        #     targets=None,
        #     sequence_length=self.seq_len,
        #     sampling_rate=self.step,
        #     batch_size=self.batch_size,
        # )
        # return dataset

    def invTransform(self, y):
        return self.data_processor.invTransform(y)
