# Shared Circular Buffer

Shared Circular Buffer is an implementation of a simple circular buffer which makes use of
[SharedMemory](https://docs.python.org/3/library/multiprocessing.shared_memory.html#multiprocessing.shared_memory.SharedMemory) in order to allow sharing of the data across multiple
python instances.

Repository: [View on GitHub](https://github.com/tandemdude/Shared-Circular-Buffer)

Docs: [View on readthedocs](https://shared-circular-buffer.readthedocs.io/en/latest/)

If you think you have found a bug or other problem with the library, or you would like to suggest a feature,
you should submit an issue on the GitHub repository [here](https://github.com/tandemdude/Shared-Circular-Buffer/issues)
Before doing so, you should make sure you are on the latest version of the library and check to see if an issue
already exists for your bug or feature.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the library.

```bash
pip install git+https://github.com/tandemdude/Shared-Circular-Buffer.git
```

## Simple Usage

There is no limit to the number of 'reader' buffer classes however there can only ever be
a single 'writer' class. If you try to write to the buffer from a read-only class an exception will
be raised and vice-versa.

Using the buffer is fairly straightforward

```python
>>> from shared_cbuff import SharedCircularBuffer
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
```

Currently, only storage of single-byte integers is supported and the buffer has a max length of 256. This is intended
to be changed in the near future.