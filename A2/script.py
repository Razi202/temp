# NAME: Razi Haider
# Assignment 2

import multiprocessing as mp
import queue
import threading
import pika

def serviceA(A, B, num_iters, q_i, q_s):
    #Establish the pika connection
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    
    #Multiply the two constants
    X = A * B
    #Run the loop till the required number of iterations.
    for i in range(num_iters):
        #calculate the value of X and pass it to the "square" function by placing the value in its queue.
        q_s.put(X)
        print(f"Value of X in service A process:{X}\n")
        #Get the updated value of 'X' from the increment queue
        X = q_i.get()
    #Sending a signol for termiation to the square function.
    #This was done because queue.empty() was logically incorrect.
    q_s.put("terminate")
    connection.close()
    
def serviceB(B, q_i, q_s):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    while True:
        #This will return us the oldest value (FCFS) in the queue and store it in X
        X = q_s.get()
        #We have to check if the first thread sent a message to terminate the code or not.
        #Note: We cannot use queue.empty() and terminate the code because the other thread might make some changes to it
        #without the current thread realizing.
        if X == "terminate":
            break
        X = X * B
        print(f"Value of X in service B process: {X}\n")
        #Now we send the value 'X' back to the increment function using its queue
        q_i.put(X)
    connection.close()
        
#A queue for the increment function
q_i = mp.Queue()
#A queue for the square function
q_s = mp.Queue()
if __name__ == "__main__":
    
    num_iters = int(input("Enter the number of iterations you want to perform:"))
    incr_thread = mp.Process(target=serviceA, args=(2, 6, num_iters, q_i, q_s))
    square_thread = mp.Process(target=serviceB, args=(6, q_i, q_s,))

    incr_thread.start()
    square_thread.start()

    incr_thread.join()
    square_thread.join()