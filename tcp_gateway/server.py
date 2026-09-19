from protocol import parse_packet
import socket
import threading
def handle_client(connection, address):
    print("Running in thread :", threading.current_thread().name)
    print("Device Connected:",address)
    buffer = b""

    try:

       while True:
           data = connection.recv(1024)
           if  not data:
              break
           buffer += data


           while b"\n" in buffer:

               raw_packet, buffer = buffer.split(b"\n",1)
               packet = raw_packet.decode("utf-8")
               try:
                  telemetry = parse_packet(packet)
                  print("Valid telemetry :",telemetry)
               except ValueError as e:
                  print("Packet rejected :",e)
    except ConnectionError as e:
        print("Connection error : ",e)

    finally:
        connection.close()
        print("Connection closed : ",address)

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server.bind(('localhost',5000))
server.listen()

print("TCP Gateway listening on port 5000")

while True:
    connection, address = server.accept()
    thread = threading.Thread(
      target = handle_client,
      args =  (connection, address)
    )

    thread.start()
