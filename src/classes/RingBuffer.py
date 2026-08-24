"""Provides a fixed-size circular buffer implementation for binary record storage."""
import struct


class RingBuffer:
    """Provides a fixed-size circular buffer implementation for binary record storage."""

    def __init__(self, capacity: int, record_format: str):
        """
        Initialize the ring buffer with a given capacity and record format.

        :param capacity: maximum number of records the buffer can hold.
        :param record_format: struct format string defining the binary layout of each record.
        :return:
        """
        if capacity <= 0:
            raise ValueError("capacity must be > 0")

        self.record_format = record_format
        self.record_size = struct.calcsize(record_format)
        self.capacity = capacity

        self.buffer = bytearray(self.record_size * capacity)
        self.head = 0
        self.tail = 0
        self.count = 0

    def is_empty(self) -> bool:
        """
        Check if the buffer contains no records.

        :return: True if buffer is empty, False otherwise.
        """
        return self.count == 0

    def is_full(self) -> bool:
        """
        Check if the buffer has reached its maximum capacity.

        :return: True if buffer is full, False otherwise.
        """
        return self.count == self.capacity

    def clear(self) -> None:
        """
        Reset the buffer to an empty state without deallocating memory.

        :return:
        """
        self.head = 0
        self.tail = 0
        self.count = 0

    def push(self, *values) -> bool:
        """
        Add a new record to the buffer if space is available.

        :param values: values to pack into the binary record according to record_format.
        :return: True if record was added, False if buffer is full.
        """
        if self.is_full():
            return False

        offset = self.head * self.record_size
        struct.pack_into(self.record_format, self.buffer, offset, *values)

        self.head = (self.head + 1) % self.capacity
        self.count += 1

        return True

    def pop(self):
        """
        Remove and return the oldest record from the buffer.

        :return: tuple of unpacked values, or None if buffer is empty.
        """
        if self.is_empty():
            return None

        offset = self.tail * self.record_size
        item = struct.unpack_from(self.record_format, self.buffer, offset)

        self.tail = (self.tail + 1) % self.capacity
        self.count -= 1

        return item

    def peek(self):
        """
        Return the oldest record without removing it from the buffer.

        :return: tuple of unpacked values, or None if buffer is empty.
        """
        if self.is_empty():
            return None

        offset = self.tail * self.record_size
        return struct.unpack_from(self.record_format, self.buffer, offset)

    def get_count(self) -> int:
        """
        Return the current number of records stored in the buffer.

        :return: number of records in the buffer.
        """
        return self.count

    def get_free_slots(self) -> int:
        """
        Return the number of available slots for new records.

        :return: number of free slots in the buffer.
        """
        return self.capacity - self.count

    def pop_bytes(self, max_records: int | None = None):
        """
        Remove and return raw binary data for up to max_records records.

        :param max_records: maximum number of records to pop, or None for all available.
        :return: bytes object containing packed binary data, or None if buffer is empty.
        """
        if self.is_empty():
            return None

        if max_records is None or max_records > self.count:
            max_records = self.count

        first_chunk_records = min(max_records, self.capacity - self.tail)
        first_chunk_start = self.tail * self.record_size
        first_chunk_end = first_chunk_start + first_chunk_records * self.record_size

        data = bytes(self.buffer[first_chunk_start:first_chunk_end])

        self.tail = (self.tail + first_chunk_records) % self.capacity
        self.count -= first_chunk_records

        return data

    def pop_all_bytes(self):
        """
        Remove and return all records as a single contiguous bytes object.

        :return: bytes object containing all packed binary data, or None if buffer is empty.
        """
        if self.is_empty():
            return None

        parts = []

        while not self.is_empty():
            chunk = self.pop_bytes()
            if chunk:
                parts.append(chunk)

        if not parts:
            return None

        return b"".join(parts)

    def iter_pop(self):
        """
        Iterate over and remove all records from the buffer one by one.

        :return: generator yielding tuples of unpacked values.
        """
        while not self.is_empty():
            yield self.pop()

    def iter_pop_bytes(self):
        """
        Iterate over and remove all records as contiguous binary chunks.

        :return: generator yielding bytes objects.
        """
        while not self.is_empty():
            chunk = self.pop_bytes()
            if chunk:
                yield chunk
