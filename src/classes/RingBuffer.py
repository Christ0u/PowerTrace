class RingBuffer:
    def __init__(self, size):
        self.size = size
        self.data = [None] * size
        self.head = 0
        self.tail = 0
        self.count = 0

    def push(self, item) -> bool:
        if self.count == self.size:
            return False  # full buffer

        self.data[self.head] = item
        self.head = (self.head + 1) % self.size
        self.count += 1

        return True

    def pop(self):
        if self.count == 0:
            return None

        item = self.data[self.tail]
        self.tail = (self.tail + 1) % self.size
        self.count -= 1

        return item

    def is_empty(self) -> bool:
        return self.count == 0
