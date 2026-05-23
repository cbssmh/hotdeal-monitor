import fcntl
import os
import sys
from scheduler import start_scheduler

LOCK_FILE = "/tmp/server-hotdeal-backup.lock"
lock_handle = None


def acquire_lock():
    global lock_handle
    lock_handle = open(LOCK_FILE, "w")
    try:
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("이미 실행 중인 프로세스가 있어 종료합니다.")
        sys.exit(1)

    lock_handle.write(str(os.getpid()))
    lock_handle.flush()

if __name__ == "__main__":
    acquire_lock()
    start_scheduler()
