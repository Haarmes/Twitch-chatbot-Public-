import socket
import struct
import pickle
import wave
import pyaudio


def audio_socket():
    while True:
        client_socket, addr = audio_sock.accept()
        print("Got connection from", addr)
        if client_socket:
            wf = wave.open(sound_file, "rb")
            p = pyaudio.PyAudio()
            # stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
            #               channels=wf.getnchannels(),
            #               rate=wf.getframerate(),
            #               input=True,
            #               frames_per_buffer=CHUNK)
            while True:

                data = wf.readframes(CHUNK)
                print(data)
                if data == b"":
                    break
                a = pickle.dumps(data)
                message = struct.pack("Q", len(a))+a
                client_socket.sendall(message)


# create audio command socket
audio_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
audio_sock_hostname = socket.gethostname()
print(audio_sock_hostname)
audio_sock_hostnameip = "65.21.246.225"
audio_sock_port = 9996
CHUNK = 1024
sound_file = "./Sound/audio1.wav"
socket_address = (audio_sock_hostnameip, audio_sock_port)

# Binding socket
audio_sock.bind(socket_address)
audio_sock.listen(5)
print("listening at:", socket_address)

audio_socket()
