import time
import random
import streamlit as st
import pandas as pd
import requests
import datetime

st.set_page_config(layout="wide")
menu = [
    "Test",
    "Metrics",
    "Nodes",
] 
page = st.sidebar.selectbox("Menu", menu)

def view_metrics():
    st.title('Metrics Dashboard')
    #   st.write(str(random.randint(3, 9)))
    placeholder = st.empty()
    try:
        d = requests.get('http://127.0.0.1:5000/get_metrics')
    except:
        st.write("Server is down")
        return 
    metrics = d.json()

    with placeholder.container():
        for test_id in metrics.keys():
            st.subheader(test_id)
            df = pd.DataFrame(metrics[test_id])
            st.write(df)

def view_nodes():
    st.title("Nodes Status")
    #   st.write(str(random.randint(3, 9)))
    placeholder = st.empty()
    while True:
        try:
            d = requests.get(f'http://127.0.0.1:5000/get_nodes')
        except:
            placeholder = st.empty()
            st.write("Server is down")
            return 
        try:
            nodes = d.json()
        except:
            placeholder = st.empty()
            continue

        with placeholder.container():
            for test_id in nodes.keys():
            #     st.subheader(test_id)
                nodes[test_id] = {"Last Updated": datetime.datetime.fromtimestamp(nodes[test_id]['last_updated']), "Node IP":nodes[test_id]['node_IP'], "Status": nodes[test_id]['status']}
            #     df = pd.DataFrame(node_ans, index=[test_id])
            #     st.write(df)
            df = pd.DataFrame(nodes)
            st.write(df)
        time.sleep(1)

def results(test_id):
    st.title(test_id)
    #   st.write(str(random.randint(3, 9)))
    placeholder = st.empty()
    while True:
        d = requests.get(f'http://127.0.0.1:5000/get_metrics/{test_id}')
        try:
            l = d.json()
        except:
            continue

        df = pd.DataFrame(l)
        with placeholder.container():
            st.write(df)
        time.sleep(1)


def req():
    st.title('Test Configuration')

    col1, col2 = st.columns(2)    

    with col1:
        test_type = st.radio(
            "Select Test",
            key="visibility",
            options=["Avalanche", "Tsunami"],
        )

        messages = st.number_input("Number of messages per driver", min_value=1, step=1, value=1, key="messages")
        if test_type == "Tsunami":
            delay = st.number_input("Delay between messages", min_value=1, step=1, value=1, key="delay")

    if st.button("Submit"):
        if test_type == 'Avalanche':
            res = requests.get(f'http://127.0.0.1:5000/avalanche?messages_per_driver={str(messages)}')
        else:
            res = requests.get(f'http://127.0.0.1:5000/tsunami?delay={str(delay)}&messages_per_driver={str(messages)}')

        test_id = res.text
        # st.print(test_id)
        results(test_id)

if page == "Metrics":
    view_metrics()
elif page == "Nodes":
    view_nodes()
elif page == "Test":
    req()