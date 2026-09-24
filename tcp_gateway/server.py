from protocol import parse_packet
from queue import Queue
from db import get_connection
import time
import socket
import threading
import signal

telemetry_queue = Queue()
shutdown_event = threading.Event()

def shutdown_handler(signum,frame):
    print("\n shutdown signal received")
    shutdown_event.set()
    telemetry_queue.put(None)


def handle_client(connection, address):
    print("Running in thread :", threading.current_thread().name)
    print("Device Connected:",address)
    buffer = b""
    try:
       while not shutdown_event.is_set():
          try:
             data = connection.recv(1024)
          except socket.timeout:
             continue
          if not data:
             break
          buffer += data
          while b"\n" in buffer:
              raw_packet, buffer = buffer.split(b"\n",1)
              packet = raw_packet.decode("utf-8")
              try:
                 telemetry = parse_packet(packet)
                 telemetry_queue.put(telemetry)
                 print("telemetry added to queue  | Queue size :",telemetry_queue.qsize())
              except ValueError as e:
                 print("Packet rejected :",e)
    except ConnectionError as e:
        print("Connection error : ",e)

    finally:
         connection.close()
         print("Connection closed : ",address)

def process_telemetry():
   db_connection = get_connection()
   while True:
        telemetry =telemetry_queue.get()
        if telemetry is None:
           telemetry_queue.task_done()
           break
        try:
            with db_connection.cursor() as cursor:
                cursor.execute(
                   """
                   INSERT INTO telemetry
                   (device_id, timestamp, temperature, humidity,
                    voltage, payload,checksum)
                   VALUES(%s, %s , %s, %s, %s ,%s,%s)
                   """,
                   (
                        telemetry["device_id"],
                        telemetry["timestamp"],
                        telemetry["temperature"],
                        telemetry["humidity"],
                        telemetry["voltage"],
                        telemetry["payload"],
                        telemetry["checksum"]
                   )
                )
            db_connection.commit()
            print("telemetry stored in database : ", telemetry)
        except Exception as e:
            db_connection.rollback()
            print("Database error :",e)
        finally:
            telemetry_queue.task_done()
   db_connection.close()
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('localhost',5000))
server.listen()
server.settimeout(1)

print("TCP Gateway listening on port 5000")

consumer_thread = threading.Thread(target = process_telemetry)
consumer_thread.start()

client_threads=[]

while not shutdown_event.is_set():
    try:
       client_socket, address = server.accept()
    except socket.timeout:
       continue
    thread = threading.Thread(
     target = handle_client,
     args =  (client_socket, address)
    )
    thread.start()
    client_threads.append(thread)

print("Waiting for client thread")

for thread in client_threads:
    thread.join()

print("Client threads stopped")

print("Waiting for consumer thread")
consumer_thread.join()
print("consumer thread stopped")
server.close()
print("Server socket closed")
print("Shutdown complete")
