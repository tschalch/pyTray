import dataStructures
import logging, os

log = logging.getLogger("tray_item")
log.setLevel(logging.WARN)

class TrayItem:
    """
    Parent Class for all items in a tray.
    """

    def __init__(self):
        self.selected = False
        self.changed = False
        dataStructures.changingItems.append(self)
        self.fields = []

    def SetSelected(self, value):
        self.selected = value

    def SetChanged(self, state):
        self.changed = state
        if state:
            #import traceback
            #traceback.print_stack()
            log.debug("TrayItem change registered for %s", self.element)

    def Clone(self):
        clone = TrayItem()
        clone.selected = self.selected
        clone.data = self.data.copy()
        clone.fields = self.fields
        return clone
    
