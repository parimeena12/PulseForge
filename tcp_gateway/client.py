import socket
import time

HOST = "localhost"
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((HOST, PORT))
    print("Connected to TCP Gateway")

    while True:
        packet = b"PF01|device-001|123|25.5|60.0|12.0|ABC|184\n"

        client.send(packet)

        print("Packet sent:", packet)

        time.sleep(2)

except ConnectionError as e:
    print("Connection error:", e)

finally:
    client.close()
    print("Client connection closed")
