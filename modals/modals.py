from modals.popup.popup import Popup



class Modals(object):
    def __init__(self, connector=None):
        self._connector = connector

        self.popup = Popup(connector)