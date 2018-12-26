import threading
import datetime

class Worker:
    thread = None
    threadId = 0

    def __init__(self, environment, queue, threadId):
        self.queue = queue
        self.environment = environment
        self.threadId = threadId

    def Start(self):
        self.thread = threading.Thread(target=self.worker)
        self.thread.start()

    def Join(self):
        self.thread.join()

    def worker(self):
        start = datetime.datetime.now()
        while True:
            ellapsedMs = (datetime.datetime.now() - start).total_seconds() * 1000
            if ellapsedMs > (self.environment.MAX_SECONDS_PER_THREAD - self.environment.HTTP_TIMEOUT) * 1000:
                break
            item = self.queue.get()
            if item is None:
                break
            item.Run(self.environment)

    def RunWorkers(environment, queue):
        workers = []
        for i in range(environment.WORKER_THREADS):
            w = Worker(environment, queue, len(workers));
            workers.append(w)
            w.Start()
        # espera a que los threads terminen
        for w in workers:
            w.Join()


    def AppendFinalizerItems(q, environment):
        # se asegura de que la cola no bloquee los threads
        q.put(None)
        for i in range(environment.WORKER_THREADS):
            q.put(None)

    def EmptyQueue(q):
        remaining = 0
        while True:
            item = q.get()
            if item is None:
                break
            remaining += 1
        return remaining
       