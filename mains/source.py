from typing import Union

class Source(object):
    def __init__(self):
        self._current: str = ""
        self._previous: Union[str, None] = None

    @property
    def current(self):
        return self._current
    
    @current.setter
    def current(self, value):
        self.previous = self._current
        self._current = value

    @property
    def previous(self):
        return self._previous
    
    @previous.setter
    def previous(self, value):
        self._previous = value