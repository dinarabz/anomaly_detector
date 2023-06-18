import paho.mqtt.subscribe as subscribe
import streamlit as st
from streamz import Stream

broker = "mqtt.cloud.uiam.sk"
port = 1883
topics = ["shellies/Shelly_Kitchen-C_CoffeMachine/relay/0/power"]

chart = st.line_chart()


def update_chart(x, chart):
    print(f"We wanna update chart with {x}")
    chart.add_rows({k: [v] for k, v in x.items()})


def handle_message(client, userdata, message, s):
    data = message.payload.decode('utf-8')
    print("%s : %s" % (message.topic, data))
    s.emit({message.topic: data})


s = Stream()
s = s.map(lambda x: {'data': x})
s.sink(update_chart, chart)

subscribe.callback(
    lambda x, y, z: handle_message(x, y, z, s), topics,
    hostname=broker, clean_session=True)
