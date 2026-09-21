import socket
import time
import sys
from protocol import build_packet

device_id = sys.argv[1]

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

client.connect(('localhost',5000))

print(f"{device_id} Connected to gateway")

packet = build_packet( device_id, 123,25.5,60.0,12.0,"ABC")
try:
   while True:
      client.send(packet.encode("utf-8"))

      print(f"{device_id}: Telemetry sent")

      time.sleep(0.5)
except KeyboardInterrupt:
   print(f"{device_id} shutting down")

finally:
   client.close()
