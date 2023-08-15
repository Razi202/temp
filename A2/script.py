import multiprocessing as mp
import pika

def serviceA(A, B, num_iters, event1, event2):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='qA')
    channel.queue_declare(queue='qB')

    X = A * B
    for i in range(num_iters):
        channel.basic_publish(exchange='', routing_key='qA', body=str(X))
        print(f"Value of X in service A process: {X}\n")
        event1.set()

        # Wait for service B to finish processing
        event2.wait()
        event2.clear()

        _, _, X = channel.basic_get(queue='qB')
        X = int(X) * B

    channel.queue_delete(queue='qA')
    channel.queue_delete(queue='qB')
    connection.close()

def serviceB(B, event1, event2):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='qA')
    channel.queue_declare(queue='qB')

    while True:
        event1.wait()
        event1.clear()
        
        # Ensure that service A has sent data to the queue
        method_frame, header_frame, body = channel.basic_get(queue='qA')
        X = int(body)
        
        # Square the value extracted from service A
        X = X ** 2
        print(f"Value of X in service B process: {X}\n")
        
        # Send the squared value back to service A
        channel.basic_publish(exchange='', routing_key='qB', body=str(X))
        
        # Signal service A to continue and wait for its signal
        event2.set()
        event1.wait()
        event1.clear()

    channel.queue_delete(queue='qA')
    channel.queue_delete(queue='qB')
    connection.close()

if __name__ == "__main__":
    num_iters = int(input("Enter the number of iterations you want to perform:"))

    event1 = mp.Event()
    event2 = mp.Event()

    incr_thread = mp.Process(target=serviceA, args=(2, 6, num_iters, event1, event2))
    square_thread = mp.Process(target=serviceB, args=(6, event1, event2))

    incr_thread.start()
    square_thread.start()

    event1.set()
    incr_thread.join()
    square_thread.join()
