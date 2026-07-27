import struct


class RingBuffer:
    def __init__(self, capacity: int, record_format: str):
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
        return self.count == 0

    def is_full(self) -> bool:
        return self.count == self.capacity

    def clear(self) -> None:
        self.head = 0
        self.tail = 0
        self.count = 0

    def push(self, *values) -> bool:
        if self.is_full():
            return False

        offset = self.head * self.record_size
        struct.pack_into(self.record_format, self.buffer, offset, *values)

        self.head = (self.head + 1) % self.capacity
        self.count += 1

        return True

    def pop(self):
        if self.is_empty():
            return None

        offset = self.tail * self.record_size
        item = struct.unpack_from(self.record_format, self.buffer, offset)

        self.tail = (self.tail + 1) % self.capacity
        self.count -= 1

        return item

    def peek(self):
        if self.is_empty():
            return None

        offset = self.tail * self.record_size
        return struct.unpack_from(self.record_format, self.buffer, offset)

    def get_count(self) -> int:
        return self.count

    def get_free_slots(self) -> int:
        return self.capacity - self.count

    def pop_bytes(self, max_records: int | None = None):
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
        while not self.is_empty():
            yield self.pop()

    def iter_pop_bytes(self):
        while not self.is_empty():
            chunk = self.pop_bytes()
            if chunk:
                yield chunk
