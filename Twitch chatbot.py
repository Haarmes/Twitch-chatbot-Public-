'''
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at
    http://aws.amazon.com/apache2.0/
or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
'''

import random
import mysql.connector
import json
import socket
import threading
import time
import wave
import struct
import pickle
import pyaudio
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.markdown import Markdown


console = Console()
i = 0
name_list = []
command_list = []
timed_messages = []

layout = Layout()
layout.split_column(Layout(name="upper"), Layout(name="lower", size=4))
layout["upper"].visible = False
print(layout)


def load_json_file():
    print("Reading information from config.json")
    with open("config.json", "r") as file:
        data = json.load(file)
        return data


def print_message(message):
    global i
    global console
    message = str(time_now()) + message
    console.print(message)


def time_now():
    now = datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S ")


def check_name(name):
    global name_list
    if name not in name_list:
        print("New name found", name, type(name))
        name_list.append(name)
        add_to_SQL(name)
        print("name added to MySQL")

        sock.send((f"PRIVMSG {channel} :Hey {name}!\n").encode("utf-8"))


def get_timed_messages_from_SQL():
    global timed_messages
    print("Getting timed messages")
    mycursor.execute("SELECT message FROM Timed_Messages")
    for tuple in mycursor:
        timed_messages.append(tuple)


def get_commands_from_SQL():
    global command_list
    print("Getting commands")
    mycursor.execute("SELECT name, response , tags FROM Commands")
    for tuple in mycursor:
        command_list.append(tuple)


def send_message_to_socket(name, message):
    if client_text_socket:
        print("client active! sending message to client")
        message_data = name + " " + message
        message_data_encode = message_data.encode()
        message_data_bytes = bytes(message_data_encode)
        message_data_struct = struct.pack("200s", message_data_bytes)
        client_socket.send(bytes(message_data_struct, "utf-8"))
        print("message send to", client_socket)


def send_audio_to_socket(audiofile):

    if client_socket:
        wf = wave.open(audiofile, "rb")
        p = pyaudio.PyAudio()
        # stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
        #                channels=wf.getnchannels(),
        #                rate=wf.getframerate(),
        #                input=True,
        #                frames_per_buffer=CHUNK)
        while True:

            data = wf.readframes(CHUNK)
            print(data)
            if data == b"":
                break
            a = pickle.dumps(data)
            message = struct.pack("Q", len(a))+a
            client_socket.sendall(message)


def check_for_command(message):
    print("Checking for command")
    print(message)
    global command_list
    i = 0
    print(command_list)
    message_split = message
    for commands in command_list:
        if commands[0] == message_split[1:-2]:
            print("Command found!")
            if "sound" in commands[2]:
                send_audio_to_socket(commands[1])
            else:
                sock.send(
                    (f"PRIVMSG {channel} : {command_list[i][1]}\n").encode("utf-8"))
        i += 1


# Threat 5: Text socket

def message_socket():
    while True:
        global client_text_socket
        client_text_socket, addr = text_sock.accept()
        print("Got text connection from", addr)


# Threat 4: Audio socket


def audio_socket():
    while True:
        global client_socket
        client_socket, addr = audio_sock.accept()
        print("Got audio connection from", addr)


# Threat 3: Time monitoring


def time_loop():
    start_time = time.time()
    print("Time_loop active")
    time.sleep(1)
    while True:
        stop_time = time.time()
        if (int(stop_time) - int(start_time)) % 1800 == 0:
            print(stop_time - start_time)
            sock.send(
                (f"PRIVMSG {channel} : {timed_messages[random.randint(0, len(timed_messages)-1)][0]}\n").encode("utf-8"))
            random.randint(0, len(timed_messages))
        time.sleep(1)


# Threat 2: Monitor terminal inputs --------- DISABLED
def send_message():
    allow_sending = False
    while True:
        message = str(input(""))
        if message == "aktivoi":
            allow_sending = True
            continue
        if allow_sending == True:
            sock.send((f"PRIVMSG {channel} :{message}\n").encode("utf-8"))


# Threat 1: Check incoming "messages"
def check_messages():
    individual_data_from_resp = {}
    while True:
        resp = sock.recv(2048).decode("utf-8")
        if resp.find("PING") != -1:
            print("found ping!")
            sock.send((f"PONG :tmi.twitch.tv\r\n").encode("utf-8"))
            print("sent pong!")
            continue
        print(resp)
        resp = resp.split(" ")
        resp[3:len(resp)] = [" ".join(resp[3:len(resp)])]
        if resp[0][0] == ":":
            individual_data_from_resp["name"] = resp[0][1:].split("!")[0]
            check_name(individual_data_from_resp["name"])
            individual_data_from_resp["channel"] = resp[2]
            individual_data_from_resp["message"] = resp[3][1:]
            if individual_data_from_resp["message"][0] == "!":
                check_for_command(individual_data_from_resp["message"])
            add_message_SQL(
                individual_data_from_resp["name"], individual_data_from_resp["message"])
            print_message(str(individual_data_from_resp["channel"] + " - " +
                              individual_data_from_resp["name"] + ": " + individual_data_from_resp["message"]))
            send_message_to_socket(
                individual_data_from_resp["name"],
                individual_data_from_resp["message"]
            )


def get_sql_names():
    print("Getting known names from MySQL")
    global name_list
    mycursor.execute("SELECT name FROM Chatter")
    for name in mycursor:
        print(type(name))
        name_list.append(str(name[0]))
    print(name_list)


def print_SQL_messages():
    mycursor.execute("SELECT * FROM Messages")
    for x in mycursor:
        print(x)


def print_SQL_name():
    mycursor.execute("SELECT * FROM Chatter")
    for x in mycursor:
        print(x)


def add_to_SQL(name: str):
    mycursor.execute(
        "INSERT INTO Chatter (name, lvl) VALUES (%s,%s)", (name, 1))
    db.commit()


def add_message_SQL(chatter_name: str, message_to_save: str):
    mycursor.execute("INSERT INTO Messages (name, time, message) VALUES (%s,%s,%s)",
                     (chatter_name, datetime.now(), message_to_save[:-2]))
    db.commit()


def check_name_id(chatter_name: str):
    mycursor.execute(f"SELECT {chatter_name}, id FROM Chatter")
    for id in mycursor:
        print(id)


# Read config.json
data = load_json_file()


# SQL connection
print("Connecting to MySQL")
db = mysql.connector.connect(
    host=str(data["data"][1]["host_name"]),
    user=str(data["data"][1]["user_name"]),
    passwd=str(data["data"][0]["password"]),
    database="test")
mycursor = db.cursor()
get_sql_names()
get_commands_from_SQL()
get_timed_messages_from_SQL()

# Socket information (Twitch)
server = "irc.chat.twitch.tv"
port = 6667
nickname = "haamsterbot"
token = data["data"][0]["token"]
channel = "#haarmes"


# Connect to socket (Twitch)
print("Connecting to Twitch socket")
sock = socket.socket()
sock.connect((server, port))
sock.send(f"PASS {token}\n".encode("utf-8"))
sock.send(f"NICK {nickname}\n".encode("utf-8"))
sock.send(f"JOIN {channel}\n".encode("utf-8"))
resp = sock.recv(2048).decode("utf-8")
print_message(resp)
resp = sock.recv(2048).decode("utf-8")
print_message(resp)


##### AUDIO #####

# create audio command socket
audio_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
audio_sock_hostname = socket.gethostname()
print(audio_sock_hostname)
audio_sock_hostnameip = "65.21.246.225"
audio_sock_port = 9996
CHUNK = 1024
socket_address = (audio_sock_hostnameip, audio_sock_port)

# Binding socket
audio_sock.bind(socket_address)
audio_sock.listen(5)
print("listening audio sockets at:", socket_address)

# text socket
text_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
text_sock_port = 9994
socket_text_address = (audio_sock_hostnameip, text_sock_port)
client_text_socket = False
text_sock.bind(socket_text_address)
text_sock.listen(5)
print("Listening for text sockets", socket_text_address)

# Threading
print("Establishing Threads for checking and sending messages")
t1 = threading.Thread(target=check_messages)
t2 = threading.Thread(target=send_message)
t3 = threading.Thread(target=time_loop)
t4 = threading.Thread(target=audio_socket)
t5 = threading.Thread(target=message_socket)
t1.start()
# Disabled t2
t3.start()
t4.start()
t5.start()
