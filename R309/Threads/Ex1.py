import threading
import time
def task(id):
    for i in range(5):
        print(f"Je suis la thread {id}")
        time.sleep(1)


if __name__ == '__main__':
    t1 = threading.Thread(target=task, args=[1])
    t2 = threading.Thread(target=task, args=[2])
    t1.start()
    t2.start()
    t1.join()
    t2.join()
