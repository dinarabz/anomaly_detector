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
    if isinstance(x, pd.Series):
        return {"data": x['_value']}
    elif isinstance(x, tuple) and isinstance(x[1], pd.Series):
        return {"data": x[1]['_value']}
    elif isinstance(x, dict):
        return list(x.values())[0]
    elif isinstance(x, MQTTMessage):
        return {"data": float(x.payload)}


def fit_transform(x, model):
    is_anomaly = model.process(x)
    return {
        "data": x.pop("data"),
        "anomaly": is_anomaly,
    }


def dump_to_file(x):
    with open("data/anomaly_detection_result.json", 'a') as f:
        print(json.dumps(x), file=f)


# def return_summary(df):
#     text = (
#         f"Proportion of anomalous samples: "
#         f"{sum(df['anomaly']) / len(df['anomaly']) * 100:.02f}%\n"
#         f"Total number of anomalous events: "
#         f"{sum(pd.Series(df['anomaly']).diff().dropna() == 1)}")
#     return text


def signal_handler(sig, frame):
    # Get the current session state
    session_state = st.session_state.get(source=None, data=None)

    # Stop the data source if it exists
    if session_state.source is not None:
        os.write(sys.stdout.fileno(), b"\nSignal received to stop the app...\n")
        session_state.source.stop()

        time.sleep(1)

        # Print summary if data exists
        if session_state.data is not None:
            if isinstance(session_state.data, pd.DataFrame):
                print(session_state.data)
            else:
                print(type(session_state.data))

        # Clear the session state
        session_state.source = None
        session_state.data = None

    exit(0)


def process_limits_streaming(data: Union[dict, pd.DataFrame]):
    anomaly_detector = MyOneClassSVM()
    st.sidebar.subheader("MQTT Settings")

    if isinstance(data, dict):
        source = Stream.from_mqtt(**data)
    elif isinstance(data, pd.DataFrame):
        source = Stream.from_iterable(data.iterrows())
    else:
        raise RuntimeError("Wrong data format.")

    detector = source.map(preprocess).map(fit_transform, anomaly_detector)

    if isinstance(data, str):
        detector.map(lambda x: json.dumps(x)).to_mqtt(mqtt_settings['host'], mqtt_settings['port'],
                                                       f"{mqtt_topic.rsplit('/', 1)[0]}/dynamic_limits",
                                                       publish_kwargs={"retain": True})
    elif isinstance(data, pd.DataFrame):
        detector.sink(dump_to_file)

    return detector


st.title("Anomaly Detection with Streamlit")

data_type = st.radio("Select data type", ("MQTT Topic", "JSON/CSV file"))

chart = st.line_chart(pd.DataFrame({'data': [], 'anomaly': []}))


def update_chart(x):
    print(f"We wanna update chart with {x}")
    chart.add_rows({k: [v] for k, v in x.items()})


if data_type == "MQTT Topic":
    st.sidebar.subheader("MQTT Settings")
    mqtt_host = st.sidebar.text_input("Host", "mqtt.example.com")
    mqtt_port = st.sidebar.number_input("Port", 1883)
    mqtt_topic = st.text_input("Enter MQTT topic")
    mqtt_settings = {
        'host': mqtt_host,
        'port': mqtt_port,
        'topic': mqtt_topic,
    }
    process_limits_streaming(mqtt_settings)

elif data_type == "JSON/CSV file":
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.json'):
            st.header('JSON file Processing')
            df = pd.read_json(uploaded_file)
            processing = process_limits_streaming(df)
            pipeline = processing.sink(update_chart)
            pipeline.start()

        elif uploaded_file.name.endswith('.csv'):
            st.header('CSV file Processing')
            df = pd.read_csv(uploaded_file)

        else:
            st.write('Upload a file with a correct format first!')
#
# if __name__ == "__main__":
#     # Set up the signal handler to stop the app gracefully
#     import signal
#
#     signal.signal(signal.SIGINT, signal_handler)
#
#     # Create a session state to hold the data source and processed data
#     st.session_state.source = None
#     st.session_state.data = None
#
#     if data_type == "MQTT Topic":
#         # Start the MQTT data source
#         st.sidebar.write("Waiting for data from MQTT topic...")
#         st.session_state.source = process_limits_streaming(mqtt_settings)
#
#     elif data_type == "JSON/CSV file":
#         # Process the data from the uplo
