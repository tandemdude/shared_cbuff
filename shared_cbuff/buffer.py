import atexit
import typing
from math import log
from multiprocessing import shared_memory

from shared_cbuff import errors

__all__: typing.List[str] = ["SharedCircularBuffer"]


def _bytes_needed(n: int) -> int:
    return 1 if n == 0 else int(log(n, 256)) + 1


class SharedCircularBuffer:
    """
    An implementation of a circular buffer built on top of :obj:`multiprocessing.shared_memory.SharedMemory` to
    allow a fast method to send and receive data between multiple python instances.

    Args:
        name (:obj:`str`): The name of the memory block, used when linking :obj:`~SharedCircularBuffer` instances
            together.

    Keyword Args:
        create (:obj:`bool`): Whether the class should create a new :obj:`~multiprocessing.shared_memory.SharedMemory`
            instance or link itself to one that already exists. Defaults to :obj:`False`
        item_size (:obj:`int`): The number of bytes each item in the buffer should take up. Defaults to ``1``.
        length (:obj:`int`): The length of the buffer. Defaults to ``2``.

    .. warning::
        All instances that connect to the same shared memory must have the ``name``, ``item_size`` and ``length``
        parameters passed in if they differ from default otherwise reading from the shared memory **will not**
        work correctly.

    """

    def __init__(
        self, name: str, *, create: bool = False, item_size: int = 1, length: int = 2
    ) -> None:
        if length < 2:
            raise ValueError("Buffer length must greater than 1")

        self.name = name
        """The name of the shared memory block this instance is attached to."""
        self.item_size = item_size
        """The maximum size of each item stored in bytes."""
        self.length = length
        """The length of the buffer."""
        self._write_pointer_byte_length = _bytes_needed(item_size * length)
        self._internal_length = (item_size * length) + self._write_pointer_byte_length
        self._writeable = create

        if create:
            self._memory = shared_memory.SharedMemory(
                name=name, create=True, size=self._internal_length
            )
        else:
            self._memory = shared_memory.SharedMemory(name=name, create=False)

        self._internal_write_pointer = 0
        self._read_pointer = 0

        atexit.register(self.cleanup)

    def __str__(self) -> str:
        if self._writeable:
            return f"SharedCircularBuffer ({self.name})"
        return f"SharedCircularBuffer ({self.name}) ({(self.usage / self.length) * 100:.2f}% full)"

    @property
    def _stored_write_pointer(self) -> int:
        return int.from_bytes(
            self._memory.buf[
                self._internal_length
                - self._write_pointer_byte_length : self._internal_length
            ],
            byteorder="big",
        )

    @_stored_write_pointer.setter
    def _stored_write_pointer(self, n: int) -> None:
        self._memory.buf[
            self._internal_length
            - self._write_pointer_byte_length : self._internal_length
        ] = n.to_bytes(self._write_pointer_byte_length, byteorder="big")

    def _next_write_pointer(self) -> None:
        self._internal_write_pointer += self.item_size
        self._internal_write_pointer %= self.length * self.item_size

        self._stored_write_pointer = self._internal_write_pointer

    def _next_read_pointer(self) -> typing.Optional[int]:
        if self._read_pointer == self._stored_write_pointer:
            return None
        self._read_pointer += self.item_size
        self._read_pointer %= self.length * self.item_size
        return self._read_pointer

    @property
    def usage(self) -> int:
        """
        The number of elements currently in the buffer. This can be used to figure out how
        full or empty the buffer is at any time.

        Returns:
            :obj:`int`: Number of items in the buffer
        """
        if self._read_pointer > self._stored_write_pointer:
            return (
                self.length
                - (self._read_pointer // self.item_size)
                + (self._stored_write_pointer // self.item_size)
            )
        return (self._stored_write_pointer - self._read_pointer) // self.item_size

    def push(self, item: int) -> None:
        """
        Pushes an item to the buffer.

        Args:
            item (:obj:`int`): The item to put into the buffer.

        Returns:
            ``None``

        Raises:
            :obj:`~.errors.WriteOperationsForbidden`: The buffer cannot be written to by this instance.
        """
        if not self._writeable:
            raise errors.WriteOperationsForbidden("Buffer is not writeable")

        self._next_write_pointer()
        temp_w_pointer = self._internal_write_pointer or (self.item_size * self.length)
        self._memory.buf[
            temp_w_pointer - self.item_size : temp_w_pointer
        ] = item.to_bytes(self.item_size, byteorder="big")

    def popitem(self) -> typing.Optional[int]:
        """
        Pops an item from the buffer.

        Returns:
            Optional[ :obj:`int` ]: Item removed from the buffer, or ``None`` if there is nothing to read.

        Raises:
            :obj:`~.errors.ReadOperationsForbidden`: The buffer cannot be read from by this instance.
        """
        if self._writeable:
            raise errors.ReadOperationsForbidden("Buffer is not readable")

        if (read_addr := self._next_read_pointer()) is not None:
            temp_r_pointer = read_addr or (self.item_size * self.length)
            return int.from_bytes(
                self._memory.buf[temp_r_pointer - self.item_size : temp_r_pointer],
                byteorder="big",
            )
        return None

    def popmany(self, n: int) -> typing.Sequence[int]:
        """
        Pops up to a maximum of ``n`` items from the buffer.

        Returns:
            Sequence[ :obj:`int` ]: Items removed from the buffer.

        Raises:
            :obj:`~.errors.ReadOperationsForbidden`: The buffer cannot be read from by this instance.
        """
        if self._writeable:
            raise errors.ReadOperationsForbidden("Buffer is not readable")

        items = []
        for _ in range(n):
            if (item := self.popitem()) is not None:
                items.append(item)
            else:
                break
        return items

    def cleanup(self) -> None:
        """
        Closes the connection to the :obj:`~multiprocessing.shared_memory.SharedMemory` block and
        unlinks it if this class was the writer to the buffer.

        This method is automatically called as long as your program exits cleanly.

        Returns:
            ``None``
        """
        self._memory.close()
        if self._writeable:
            self._memory.unlink()
