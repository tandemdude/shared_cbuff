.. Shared Circular Buffer documentation master file, created by
   sphinx-quickstart on Sun May 10 19:43:22 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg

----

Shared Circular Buffer
======================

Shared Circular Buffer is an implementation of a simple circular buffer which makes use of
:obj:`multiprocessing.shared_memory.SharedMemory` in order to allow sharing of the data across multiple
python instances.

Repository: `View on GitHub <https://github.com/tandemdude/shared_cbuff>`_

Docs: `View on readthedocs <https://shared-cbuff.readthedocs.io/en/latest/>`_

If you think you have found a bug or other problem with the library, or you would like to suggest a feature,
you should submit an issue on the GitHub repository `here <https://github.com/tandemdude/shared_cbuff/issues>`_.
Before doing so you should make sure you are on the latest version of the library and check to see if an issue
already exists for your bug or feature.


Simple Usage
============

There is no limit to the number of 'reader' buffer classes however there can only ever be
a single 'writer' class. If you try to write to the buffer from a read-only class an exception will
be raised and vice-versa.

Using the buffer is fairly straightforward
::

    >>> # Create a buffer object
    >>> scb_a = SharedCircularBuffer("shared_buffer_a", create=True, length=5)
    >>> # Link a second buffer object to the same memory block as the first
    >>> scb_b = SharedCircularBuffer("shared_buffer_a", length=5)
    >>> # Insert items into the buffer
    >>> scb_a.push(50)
    >>> scb_a.push(10)
    >>> scb_a.push(20)
    >>> scb_a.push(30)
    >>> # Extract a single item from the buffer
    >>> scb_b.popitem()
    50
    >>> # Extract multiple items from the buffer
    >>> scb_b.popmany(3)
    [10, 20, 30]

Note that currently, only integer values can be written to and read from the buffer.

**Index:**

.. toctree::
    :maxdepth: 2

    api-reference

* :ref:`genindex`