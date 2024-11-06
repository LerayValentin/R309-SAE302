import threading
import time
def task(id, x):
    print(f"thread {id} : {x}")
    for i in range(x):
        x -= 1
        print(f"thread {id} : {x}")
        time.sleep(1)

if __name__ == '__main__':
    t1 = threading.Thread(target=task, args=[1, 5])
    t2 = threading.Thread(target=task, args=[2, 10])
    t1.start()
    t2.start()
    t1.join()
    t2.join()

