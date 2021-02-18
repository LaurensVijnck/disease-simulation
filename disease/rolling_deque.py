from collections import deque
from collections import defaultdict
from datetime import datetime


class RollingDeque:
    """
    Custom data-structure to maintain a temporal
    set of deque objects.

    Note: not thread safe.
    """
    def __init__(self):
        self._counter = 0
        self._deque_map = defaultdict(deque)

    def get_elements_for_date(self, date: datetime):
        for element in self._deque_map[date]:
            self._counter -= 1
            yield element

        del self._deque_map[date]

    def put_element(self, date: datetime, element):
        self._counter += 1
        self._deque_map[date].append(element)

    def get_num_elements(self):
        return self._counter