from typing import Union
import sys
import time
import pandas as pd
import json
import os
import datetime as dt
from paho.mqtt.client import MQTTMessage
from river import anomaly
from streamz import Stream
import streamlit as st
import json

GRACE_PERIOD = 60 * 24

# st.title("Anomaly Detection with Streamlit")
# data_type = st.radio("Select data type", ("MQTT Topic", "JSON/CSV file"))
# chart = st.line_chart()


class MyOneClassSVM:
    def __init__(self, grace_period=GRACE_PERIOD):
        self.grace_period = grace_period
        self.n_samples = 0
        self.model = anomaly.QuantileFilter(
            anomaly.OneClassSVM(nu=0.2),
            q=0.995)

    def learn(self, x):
        self.n_samples += 1
        return self.model.learn_one(x)

    def score(self, x) -> float:
        return self.model.score_one(x)

    def predict(self, x):
        # if self.n_samples < self.grace_period:
        #     return 0
        score = self.score(x)
        return self.model.classify(score)

    def process(self, x):
        is_anomaly = self.predict(x)
        if not is_anomaly:
            self.learn(x)
        return is_anomaly


def preprocess(x):
    # print(x)
    # if isinstance(x, pd.DataFrame):
    if isinstance(x[1], pd.Series):
        return x
    else:
        raise RuntimeError("Wrong data format in preprocess.")
    # elif isinstance(x, tuple) and isinstance(x[1], pd.Series):
    #     print("this case 2")
    #     return {"data": x[1]['_value']}
    # elif isinstance(x, dict):
    #     print("this case")
    #     return list(x.values())[0]
    # elif isinstance(x, MQTTMessage):
    #     print("this case 3")
    #     return {"data": float(x.payload)}


def fit_transform(x, model):
    is_anomaly = model.process(x)
    return {
        "data": x.pop("data"),
        "anomaly": is_anomaly,
    }


df = pd.read_json('input_data/consumption.json')

# df.time = pd.to_datetime(df.time)
# df = df.set_index('time')
# print(df['_value'][4527])

# f = open("input_data/consumption.json")
# data = json.load(f)
# df = pd.DataFrame(data)


def dump_to_file(x):
    with open("data/anomaly_detection_result.json", 'a') as f:
        print(json.dumps(x), file=f)


def process_limits_streaming(data: pd.DataFrame):
    anomaly_detector = MyOneClassSVM()

    if isinstance(data, pd.DataFrame):
        source = Stream.from_iterable(data.iterrows())
    else:
        raise RuntimeError("Wrong data format.")

    detector = source.map(preprocess) #.map(fit_transform, anomaly_detector)
    detector.sink(print)
    source.emit(data)
    # detector.sink(dump_to_file)

    return detector


process_limits_streaming(df)


# df = pd.read_json(uploaded_file)
# processing = process_limits_streaming(df)
# pipeline = processing.sink(update_chart)
# pipeline.start()


# def update_chart(x, chart):
#     print(f"We wanna update chart with {x}")
#     chart.add_rows({k: [v] for k, v in x.items()})

#
# #DATA UPLOADER
# if data_type == "MQTT Topic":
#     pass
# elif data_type == "JSON/CSV file":
#     uploaded_file = st.file_uploader("Choose a file")
#
#     if uploaded_file is not None:
#         if uploaded_file.name.endswith('.json'):
#             st.header('JSON file Processing')
#
#
#         elif uploaded_file.name.endswith('.csv'):
#             st.header('CSV file Processing')
#
#         else:
#             st.write('Upload a file with a correct format first!')
#
