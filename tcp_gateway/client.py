import socket
import time
import sys

from protocol import build_packet

HOST = "localhost"
PORT = 5000
device_id = sys.argv[1]

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((HOST, PORT))
    print(f"{device_id} Connected to gateway")

    while True:
        packet = build_packet(device_id,123,25.5,60.0,12.0,"ABC")

        print("Sending packet:", packet)

        client.send(packet.encode("utf-8"))

        time.sleep(2)

except ConnectionError as e:
    print("Connection error:", e)

except KeyboardInterrupt:
    print("\nStopping client...")

finally:
    client.close()
    print("Client connection closed")
