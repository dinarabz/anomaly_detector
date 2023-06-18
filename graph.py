import altair as alt
import numpy as np
import paho.mqtt.subscribe as subscribe
import pandas as pd
import streamlit as st
from streamz import Stream

# st.title("Anomaly Detection with Streamlit")
# data_type = st.radio("Select data type", ("MQTT Topic", "JSON/CSV file"))
#
# df = pd.read_json('data/anomaly_detection_result.json')
#
# data = []
# for index, row in df.iterrows():
#     data.append([row['value'], row['anomaly'], row['time']])
#
# final_data = pd.DataFrame(data, columns=['value1', 'value2', 'date'])
#
#
# final_data['date'] = pd.to_datetime(final_data['date'])
#
#
# final_data.set_index('date', inplace=True)
#
# st.line_chart(final_data)



# df = pd.read_json('data/anomaly_detection_result.json')
#
# data = []
# for index, row in df.iterrows():
#     print([row['value'], row['time']])
#     data.append([row['value'], row['time']])
#
# final_data = pd.DataFrame(data, columns=['value1', 'date'])
#
#
# final_data['date'] = pd.to_datetime(final_data['date'])
#
#
# final_data.set_index('date', inplace=True)
#
# st.line_chart(final_data)



df = pd.DataFrame({
    'name': ['brian', 'dominik', 'patricia'],
    'age': [20, 30, 40],
    'salary': [100, 200, 300]
})

a = alt.Chart(df).mark_area(opacity=1).encode(
    x='name', y='age')

b = alt.Chart(df).mark_area(opacity=0.6).encode(
    x='name', y='salary')

c = alt.layer(a, b)

st.altair_chart(c, use_container_width=True)