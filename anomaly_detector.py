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

GRACE_PERIOD = 60 * 24


st.title("Anomaly Detection with Streamlit")
data_type = st.radio("Select data type", ("MQTT Topic", "JSON/CSV file"))
chart = st.line_chart()


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


def update_chart(x, chart):
    print(f"We wanna update chart with {x}")
    chart.add_rows({k: [v] for k, v in x.items()})


#DATA UPLOADER
if data_type == "MQTT Topic":
    pass
elif data_type == "JSON/CSV file":
    uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file is not None:
        if uploaded_file.name.endswith('.json'):
            st.header('JSON file Processing')


        elif uploaded_file.name.endswith('.csv'):
            st.header('CSV file Processing')

        else:
            st.write('Upload a file with a correct format first!')



