import struct
import socket


client_socket_hostname = socket.gethostname()
client_socket_hostnameip = "65.21.246.225"
print("connecting to ip", client_socket_hostnameip)

hostport = 9994
client_text_socket = socket.socket()
host_address = (client_socket_hostnameip, hostport)
client_text_socket.connect(host_address)

print("listening")

while True:

    data = b""
    payload_size = struct.calcsize("200s")
    while True:
        try:
            while len(data) < payload_size:
                packet = client_text_socket.recv(4*1024)
                print(packet)
                if not packet:
                    print("no packet")
                    break
                data += packet
        except:
            break
