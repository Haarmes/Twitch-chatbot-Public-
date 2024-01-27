import socket
import struct
import pickle
import wave
import pyaudio


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WAVE_OUTPUT_FILENAME = "output.wav"
p = pyaudio.PyAudio()
frames = []
stream = p.open(format=p.get_format_from_width(2),
                channels=2,
                rate=44100,
                output=True,
                frames_per_buffer=CHUNK)


client_socket_hostname = socket.gethostname()
client_socket_hostnameip = "65.21.246.225"
print("connecting to ip", client_socket_hostnameip)
host_port = 9996
client_socket = socket.socket()
host_address = (client_socket_hostnameip, host_port)
client_socket.connect(host_address)

print("listening...")
while True:
    data = b""
    payload_size = struct.calcsize("Q")

    while True:

        try:
            while len(data) < payload_size:
                packet = client_socket.recv(4*1024)
                print(packet)
                if not packet:
                    print("no packet")
                    break
                data += packet

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]
            while len(data) < msg_size:
                data += client_socket.recv(4*1024)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            print(frame_data)

        except:
            break
    client_socket.close()
    print('Audio closed')
    break
