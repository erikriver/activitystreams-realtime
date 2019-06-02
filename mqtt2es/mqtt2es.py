import os
import ssl
import json
import time
from datetime import datetime

import paho.mqtt.client as mqtt
from elasticsearch import Elasticsearch

# stdout
def debug(msg):
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + " " + msg, flush=True)


def on_connect(client, userdata, flags, rc):
    """
    The callback for when the client receives a CONNACK response from the server.
    """
    debug("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")

    client.subscribe("#")

def on_message(client, userdata, message):
    """
    The callback for when a PUBLISH message is received from the server.
    """
    # debug(message.topic+" "+str(message.payload))
    server_time = int(time.time()*1000)
    index = "devices_customer1" # split from topic

    # step 1: tokenize topic string with delimiter "slash"
    try:  # VIN, Subtopic und SessionID auslesen
        split_topic = str(message.topic).split("/")

        if split_topic.__len__() != 3:
            raise ValueError

        user_uuid = int(split_topic[1])
        status_type = str(split_topic[2])

    except ValueError as exception_message:
        #debug("Error evaluating topic string. Exception: " + str(exception_message) +
        #              " -- Ignoring message with topic: " + message.topic)
        return -1

    try:
        msg_json = json.loads(message.payload.rstrip(chr(0)).replace('\n',''))
    except ValueError:
        debug("JSON Error")
        return 0

    msg_json.update({"server_time": server_time})
    msg_json.update({"user_uuid": user_uuid})
    msg_json.update({"status_type": status_type})

    debug("rx message on topic: " + str(message.topic))
    es.index(index, "_doc", msg_json)


# Elasticsearch
elasticsearch_user = os.environ["ELASTICSEARCH_USER"]
elasticsearch_pass = os.environ["ELASTICSEARCH_PASS"]
elasticsearch_host = os.environ["ELASTICSEARCH_HOSTS"]

es_conn = 0
es = None
while es_conn == 0:
    try:
        es = Elasticsearch(hosts=[elasticsearch_host], timeout=60, http_auth=(elasticsearch_user, elasticsearch_pass), scheme="https", port=443)
        es_conn = 1
    except:
        debug("Error: Could not connect to Elasticsearch host.")
        es_conn = 0
        time.sleep(5)

mqtt_user = os.environ['MQTT_USER']
mqtt_pass = os.environ['MQTT_PASS']
mqtt_host = os.environ['MQTT_HOST']

client = mqtt.Client(client_id="Testclient", clean_session=True, userdata=None)
client.tls_set(ca_certs=None, cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(mqtt_user, mqtt_pass)
client.enable_logger(logger=None)
client.connect(host=mqtt_host, port=8883, keepalive=60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()




# TODO
#  If you want prepare this solution isolated witouth external ES configurations
#  
#
#  - ES Automatic Index Creation
#    https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-index_.html#index-creation
#
#    PUT _cluster/settings
#    {
#       "persistent": {
#       "action.auto_create_index": "true" 
#       }
#    }
#  - Create Index Template
#    https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-templates.html#indices-templates
# PUT _template/template_devices
# {
#   "index_patterns": ["devices_*", "pings_*"],
#   "settings": {
#     "number_of_shards": 1
#   },
#   "mappings": {
#     "_source": {
#       "enabled": false
#     },
#     "properties": {
#         "serverTime": {"type": "date", "format": "yyyy/MM/dd HH:mm:ss||epoch_millis"},
#         "docType": {"type": "keyword"},
#         "clientId": {"type": "keyword"}
#     }
#   }
# }