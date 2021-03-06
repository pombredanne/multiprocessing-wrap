# multiprocessing-wrap

[![Build Status](https://travis-ci.org/domsleee/multiprocessing-wrap.svg?branch=master)](https://travis-ci.org/domsleee/multiprocessing-wrap)
[![PyPI shield](https://img.shields.io/pypi/v/multiprocessing-wrap.svg?style=flat-square)](https://pypi.org/project/multiprocessing-wrap/)

A simple interface for writing concurrent scripts. Get the most out of `multiprocessing` without all the boilerplate and confusing syntax!

## Features

* Sensible error propagation - having a stack trace showing where your code speeds debugging and development
* Built-in loading bar as default using [tqdm](https://github.com/tqdm/tqdm)
* Uses [dill](https://github.com/uqfoundation/dill) for pickling, which extends the types that can be passed to your workers (see [here](http://docs.python.org/library/pickle.html#what-can-be-pickled-and-unpickled) for documentation of the limitations of python's default pickling)

## Installation

To install using pip:

~~~bash
pip install multiprocessing-wrap
~~~

## Usage

You can use the functional `multiprocess` for single line multiprocessing:

~~~python
from multiprocess import multiprocess

f = lambda: print(1)
multiprocess(f, [(), (), ()])
~~~

~~~bash
1  
1  
1
~~~

Otherwise you can use the `Multiprocess` class to use the more explicit `add_tasks` and `do_tasks` directives:

~~~python
from multiprocess import Multiprocess

m = Multiprocess(show_loading_bar=False)
f = lambda: print(1)
m.add_tasks(f, [(), (), ()])
m.do_tasks() # blocking
m.close()
~~~

A more involved example of sorting numbers using `sleep`. Since the worker function is run in a different process, to transfer data between the processes we use a thread-safe `Queue`. Note the following only works if you have at least 2 threads:
~~~python
from multiprocess import multiprocess, Queue
from time import sleep

def sleep_sort():
  q = Queue()
  def f(q, x):
    sleep(x)
    q.push(x)
  
  multiprocess(f, [(q, 1,), (q, 2,)])
  print('SORTED')
  while not q.empty():
    print(q.pop())

sleep_sort()
~~~

~~~bash 
1  
2
~~~

## Error handling
Errors from within a process are propagated back to the parent with stack information. For example:

~~~python
from multiprocess import Multiprocess

m = Multiprocess()
def f(x):
  raise ValueError('bad error')

m.add_tasks(f, [(1,)])
m.do_tasks()
m.close()
~~~

~~~bash
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/dom/Documents/git/Multiprocess/multiprocess/multiprocessClass.py", line 61, in do_tasks
    self._check_for_exceptions()
  File "/Users/dom/Documents/git/Multiprocess/multiprocess/multiprocessClass.py", line 79, in _check_for_exceptions
    "\n".join(['ERROR: ' + str(e) for e in exceptions]))
multiprocess.multiprocessClass.MultiprocessProcessException: 1 errors occurred:
ERROR: Error in function call "f((1,))"
Traceback (most recent call last):
  File "/Users/dom/Documents/git/Multiprocess/multiprocess/multiprocessClass.py", line 95, in my_worker
    fn(*rem_args)
  File "<stdin>", line 2, in f
ValueError: bad errorr
~~~

