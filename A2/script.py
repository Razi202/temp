# NAME: Razi Haider
# Assignment 2

import multiprocessing as mp
import queue
import threading
import pika

def serviceA(A, B, num_iters, event1, event2):
    #Establish the pika connection
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
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
        event1.set()

        #wait for service B's response
        event2.wait()
        event2.clear()

        #Get the updated value of 'X' from the service B queue
        _, _, X = channel.basic_get(queue='qB')
        #perform the second operation: X = X * B
        X = int(X) * B

    channel.queue_delete(queue="qA")
    channel.queue_delete(queue="qB")
    connection.close()
    
def serviceB(B, event1, event2):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    q_i = channel.queue_declare(queue='qA')
    q_s = channel.queue_declare(queue='qB')
    while True:
        event1.wait()
        event1.clear()
        #Get the value from service A
        _, _, X = channel.basic_get(queue='qA')
        #Square the value extracted from service A
        X = int(X) ** 2
        print(f"Value of X in service B process: {X}\n")
        #Now we send the value 'X' back to service A using its queue
        channel.basic_publish(exchange='', routing_key='qB', body=str(X))
        #service A may continue
        event2.set()
        event1.set()

    channel.queue_delete(queue="qA")
    channel.queue_delete(queue="qB")
    connection.close()
        
#A queue for the increment function
# q_i = mp.Queue()
# #A queue for the square function
# q_s = mp.Queue()

if __name__ == "__main__":
    
    event1 = mp.Event()
    event2 = mp.Event()

    num_iters = int(input("Enter the number of iterations you want to perform:"))
    incr_thread = mp.Process(target=serviceA, args=(2, 6, num_iters, event1, event2,))
    square_thread = mp.Process(target=serviceB, args=(6, event1, event2,))

    incr_thread.start()
    square_thread.start()

    event1.set()
    incr_thread.join()
    square_thread.join()
