# NAME: Razi Haider
# Assignment 2

import multiprocessing as mp
import queue
import threading
import pika

def serviceA(A, B, num_iters, event1, event2):
    #Establish RabbitMQ connection via pika
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    #Declare RabbitMQ queues
    q_i = channel.queue_declare(queue='qA')
    q_s = channel.queue_declare(queue='qB')
    
    #Multiply the two constants
    X = A * B
    #Run the loop till the required number of iterations.
    for i in range(num_iters):
        #calculate the value of X and pass it to the "service B" function by placing the value in its queue.
        channel.basic_publish(exchange='', routing_key='qA', body=str(X))
        print(f"Value of X in service A process:{X}\n")
        #servie B may start
        event2.set()
        event1.clear()

        #wait for service B's response
        event1.wait()

        #Get the updated value of 'X' from the service B queue
        _, _, X = channel.basic_get(queue='qB')
        #perform the second operation: X = X * B
        X = int(X) * B

    channel.queue_delete(queue="qA")
    channel.queue_delete(queue="qB")
    connection.close()
    
def serviceB(B, num_iters, event1, event2):
    #Establish RabbitMQ connection via pika
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    #Declare RabbitMQ queues
    q_i = channel.queue_declare(queue='qA')
    q_s = channel.queue_declare(queue='qB')
    for i in range(num_iters):
        event2.wait()
        #Get the value from service A
        _, _, X = channel.basic_get(queue='qA')
        #Square the value extracted from service A
        X = int(X) ** 2
        print(f"Value of X in service B process: {X}\n")
        #Now we send the value 'X' back to service A using its queue
        channel.basic_publish(exchange='', routing_key='qB', body=str(X))
        #service A may continue
        event1.set()
        event2.clear()

    channel.queue_delete(queue="qA")
    channel.queue_delete(queue="qB")
    connection.close()
        
if __name__ == "__main__":
    #Define events for synchronization
    event1 = mp.Event()
    event2 = mp.Event()

    num_iters = int(input("Enter the number of iterations you want to perform:"))

    #Create processes
    incr_thread = mp.Process(target=serviceA, args=(2, 6, num_iters, event1, event2,))
    square_thread = mp.Process(target=serviceB, args=(6, num_iters, event1, event2,))

    incr_thread.start()
    square_thread.start()

    event1.set()
    incr_thread.join()
    square_thread.join()
