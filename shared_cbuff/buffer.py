import atexit
import typing
from multiprocessing import shared_memory

from shared_cbuff import errors

__all__: typing.List[str] = ["SharedCircularBuffer"]


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
    ):
        if length > 256:
            raise TypeError("Buffer length must be at maximum 256")

        self.name = name
        self.item_size = item_size
        self.length = length
        self._internal_length = (item_size * length) + 1
        self.writeable = create

        if create:
            self._memory = shared_memory.SharedMemory(
                name=name, create=True, size=self._internal_length
            )
        else:
            self._memory = shared_memory.SharedMemory(name=name, create=False)

        self._write_pointer = self._memory.buf[self._internal_length - 1] = 0
        self._read_pointer = 0

        atexit.register(self.cleanup)

    def _next_write_pointer(self) -> None:
        self._write_pointer += 1
        self._write_pointer %= self.length

        self._memory.buf[self._internal_length - 1] = self._write_pointer

    def _next_read_pointer(self) -> typing.Optional[int]:
        if self._read_pointer == self._memory.buf[self._internal_length - 1]:
            return None
        self._read_pointer += 1
        self._read_pointer %= self.length
        return self._read_pointer

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
        if not self.writeable:
            raise errors.WriteOperationsForbidden("Buffer is not writeable")

        self._next_write_pointer()
        self._memory.buf[self._write_pointer] = item

    def popitem(self) -> typing.Optional[int]:
        """
        Pops an item from the buffer.

        Returns:
            Optional[ :obj:`int` ]: Item removed from the buffer, or ``None`` if there is nothing to read.

        Raises:
            :obj:`~.errors.ReadOperationsForbidden`: The buffer cannot be read from by this instance.
        """
        if self.writeable:
            raise errors.ReadOperationsForbidden("Buffer is not readable")

        if (read_addr := self._next_read_pointer()) is not None:
            return self._memory.buf[read_addr]
        return None

    def popmany(self, n: int) -> typing.Sequence[int]:
        """
        Pops up to a maximum of ``n`` items from the buffer.

        Returns:
            Sequence[ :obj:`int` ]: Items removed from the buffer.

        Raises:
            :obj:`~.errors.ReadOperationsForbidden`: The buffer cannot be read from by this instance.
        """
        if self.writeable:
            raise errors.ReadOperationsForbidden("Buffer is not readable")

        items = []
        for _ in range(n):
            if (read_addr := self._next_read_pointer()) is not None:
                items.append(self._memory.buf[read_addr])
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
        if self.writeable:
            self._memory.unlink()
