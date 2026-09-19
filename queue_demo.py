from queue import Queue
import threading
import time

q = Queue()

def producer():
    for i in range(5):
        item = f"Packet-{i}"
        print("producing:", item)

        q.put(item)
        time.sleep(1)
    q.put(None)

def consumer():
    while True:
         item = q.get()
         if item is None:
            q.task_done()
            break

         print("Consuming :", item)

         time.sleep(2)
         q.task_done()

producer_thread = threading.Thread(target=consumer)
consumer_thread = threading.Thread(target = producer)


producer_thread.start()
consumer_thread.start()

producer_thread.join()
q.join()

print("All packets processed")

