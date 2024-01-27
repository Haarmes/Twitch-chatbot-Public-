import mysql.connector
import json
from datetime import datetime

def load_json_file():
    with open("config.json" , "r") as file:
        data = json.load(file)
        return data


#Read config.json
data = load_json_file()

db = mysql.connector.connect(
    host=str(data["data"][1]["host_name"]), 
    user=str(data["data"][1]["user_name"]), 
    passwd=str(data["data"][0]["password"]),
    database="test")

mycursor = db.cursor()


mycursor.execute("INSERT INTO Timed_Messages (message) VALUES (%s)", ("",))
#mycursor.execute("CREATE TABLE Timed_Messages (message VARCHAR(255) NOT NULL, timed_message_id int PRIMARY KEY AUTO_INCREMENT)")
#mycursor.execute("INSERT INTO Commands (name, response) VALUES (%s,%s)", ("hey", "hey!"))
#mycursor.execute("CREATE TABLE Commands (name VARCHAR(50), response VARCHAR(255) NOT NULL, command_id int PRIMARY KEY AUTO_INCREMENT)")
#mycursor.execute("CREATE TABLE Chatter (name VARCHAR(50), lvl smallint UNSIGNED, id int PRIMARY KEY AUTO_INCREMENT)")
#mycursor.execute("CREATE TABLE Messages (name varchar(50) NOT NULL, time datetime NOT NULL, message varchar(255) NOT NULL, id int NOT NULL AUTO_INCREMENT PRIMARY KEY)")
#mycursor.execute("INSERT INTO Messages (name, time, message) VALUES (%s,%s,%s)", ("Haamsterbot", datetime.now(), "Hello World"))
db.commit()
