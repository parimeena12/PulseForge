from protocol import parse_packet
from queue import Queue
from db import get_connection
from logger import logger
import socket
import threading
import signal


telemetry_queue = Queue()
shutdown_event = threading.Event()


def handle_client(connection, address):
    logger.info("Device connected: %s", address)
    connection.settimeout(1)
    buffer = b""

    try:
        while not shutdown_event.is_set():
            try:
                data = connection.recv(1024)
                if not data:
                    break

                buffer += data

                while b"\n" in buffer:
                    raw_packet, buffer = buffer.split(b"\n", 1)
                    packet = raw_packet.decode("utf-8")

                    try:
                        telemetry = parse_packet(packet)

                        telemetry_queue.put(telemetry)

                        logger.info(
                            "Telemetry added to queue | Queue size: %d",
                            telemetry_queue.qsize()
                        )

                    except ValueError as e:
                        logger.warning("Packet rejected: %s", e)

            except socket.timeout:
                continue

    except ConnectionError as e:
        logger.warning(
            "Connection error from %s: %s",
            address,
            e
        )

    finally:
        connection.close()
        logger.info("Connection closed: %s", address)


def process_telemetry():
    db_connection = get_connection()

    while True:
        telemetry = telemetry_queue.get()

        if telemetry is None:
            telemetry_queue.task_done()
            break

        try:
            with db_connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO telemetry
                    (device_id, timestamp, temperature, humidity,
                     voltage, payload, checksum)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
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

            logger.info(
                "Telemetry stored in database: %s",
                telemetry
            )

        except Exception as e:
            db_connection.rollback()
            logger.error("Database error: %s", e)

        finally:
            telemetry_queue.task_done()

    db_connection.close()
    logger.info("Database connection closed")


def shutdown_handler(signum, frame):
    logger.info("Shutdown signal received")
    shutdown_event.set()


signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(("localhost", 5000))
server.listen()
server.settimeout(1)

logger.info("TCP Gateway listening on port 5000")


consumer_thread = threading.Thread(
    target=process_telemetry,
    name="TelemetryConsumer"
)

consumer_thread.start()


client_threads = []


while not shutdown_event.is_set():

    try:
        client_socket, address = server.accept()

    except socket.timeout:
        continue

    thread = threading.Thread(
        target=handle_client,
        args=(client_socket, address)
    )

    thread.start()
    client_threads.append(thread)


logger.info("Waiting for client threads")

for thread in client_threads:
    thread.join()

logger.info("Client threads stopped")


telemetry_queue.put(None)

logger.info("Waiting for consumer thread")

consumer_thread.join()

logger.info("Consumer thread stopped")


server.close()

logger.info("Server socket closed")
logger.info("Shutdown complete")
