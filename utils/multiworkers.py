from typing import Any, Callable, List
from utils import LOGGER
import multiprocessing
import threading
import time
import tqdm


__ITEMS: List[Any] = []
__LOCK = multiprocessing.Lock()
__STOP: bool = False
__WORKERS: List[Any] = []


def __use_worker(func: Callable[[int], bool], id: int) -> None:
    global __ITEMS
    global __LOCK
    global __STOP
    global __WORKERS

    isSuccess: bool = False
    worker: int = -1

    try:
        while not __STOP and worker == -1:
            with __LOCK:
                worker = next((i[0] for i in __WORKERS if i[1]), -1)

                if worker != -1:
                    LOGGER.debug(f"{id}: Locking Worker, Worker='{worker}'")
                    __WORKERS[worker][1] = False
            if worker == -1:
                time.sleep(1)

        if __STOP:
            raise KeyboardInterrupt

        try:
            isSuccess = func(worker, id)
        except Exception as e:
            LOGGER.error(f"{id}: Failed to Get Result, {e}")
        finally:
            with __LOCK:
                LOGGER.debug(f"{id}: isSuccess='{isSuccess}'")
                __ITEMS[id][1] = isSuccess

                LOGGER.debug(f"{id}: Unlocking Worker, Worker='{worker}'")
                __WORKERS[worker][1] = True
    except KeyboardInterrupt:
        LOGGER.debug(f"{id}: Keyboard Interrupt, isSuccess='{isSuccess}'")
        return


def multiworkers(func: Callable[[int], bool]) -> Callable[[Any], None]:
    def wrapper(**kwargs) -> None:
        global __ITEMS
        global __STOP
        global __WORKERS

        __ITEMS = kwargs["items"]
        __WORKERS = [[i, True] for i in range(kwargs["workers"])]
        threads: List[threading.Thread] = [threading.Thread(args=(func, i[0]), target=__use_worker) for i in __ITEMS]

        for thread in threads:
            thread.start()

        try:
            with tqdm.tqdm(total=len(threads)) as pbar:
                for thread in threads:
                    thread.join()
                    pbar.update(1)
        except KeyboardInterrupt:
            LOGGER.warning("Keyboard Interrupt")
            __STOP = True

    return wrapper
