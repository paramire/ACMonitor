from threading import Thread
from time import sleep

def threaded_function(arg):
    for i in range(arg):
        print "running 1"
        sleep(1)

def threaded2_function(arg,arg2):
    print arg
    print arg2


if __name__ == "__main__":
    thread = Thread(target = threaded_function, args = (10, ))
    thread2 = Thread(target = threaded2_function, args = (11,2,))
    thread.start()
    thread2.start()
    thread.join()
    print "thread finished...exiting"