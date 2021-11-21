from multiprocessing import Process
import os
import subprocess


def start_frontend():
    subprocess.call(['npm', 'run', 'serve'], cwd='frontend')


def start_backend():
    subprocess.call(['python', 'app.py'], cwd='backend')


if __name__ == '__main__':
    p1 = Process(target=start_frontend)
    p1.start()
    p2 = Process(target=start_backend)
    p2.start()
    
    p1.join()
    p2.join()
