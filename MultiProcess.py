from tqdm import tqdm
import multiprocessing

MANAGER = multiprocessing.Manager()

class MultiProcessException(Exception):
  pass

class MultiProcess:
  def __init__(self, show_loading_bar=True):
    self.pool = multiprocessing.Pool()
    self.jobs = []
    self.show_loading_bar = show_loading_bar
    self.errQ = Queue()

  def _reset(self):
    while not self.errQ.empty():
      self.errQ.pop()
    self.jobs = []

  def add_tasks(self, fn, arr_of_args):
    """add tasks to be done"""
    self.jobs += [(fn, self.errQ) + args for args in arr_of_args]

  def do_tasks(self):
    """Block the thread and complete the tasks"""
    job_count = len(self.jobs)
    if self.show_loading_bar:
      pbar = tqdm(total=job_count)

    if not self.show_loading_bar:
      self.pool.imap_unordered(my_worker, self.jobs)
    else:
      for _ in enumerate(self.pool.imap_unordered(my_worker, self.jobs)):
        pbar.update(1)
    
    pbar.close()

    # Raise exceptions, if there were any
    if not self.errQ.empty():
      exceptions = []
      while not self.errQ.empty():
        exceptions.append(self.errQ.pop())
      raise MultiProcessException('%s errors occurred:\n' % len(exceptions) + "\n".join(['ERROR: ' + str(e) for e in exceptions]))
    
    self._reset() 
  
  def close(self):
    self.pool.close()


def my_worker(args):
  fn = args[0]
  errQ = args[1]
  remArgs = args[2:]
  try:
    fn(*remArgs)
  except Exception as e:
    errQ.push(e)


"""A lightweight wrapper for multiprocess.manager.Queue()"""
class Queue:
  def __init__(self):
    self.q = MANAGER.Queue()
    #for method in dir(self.q):
    #  if method[0] != '_':
    #    setattr(self, method, getattr(self.q, method]))
  
  def get(self):
    return self.q.get()
  
  def put(self, v):
    self.q.put(v)

  def pop(self):
    return self.get()
  
  def push(self, v):
    self.q.put(v)
  
  def empty(self):
    return self.q.empty()
