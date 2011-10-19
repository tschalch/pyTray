class TrayError(Exception):
    def __init__(self, value, caller=None):
        self.value = value
        self.caller = caller
    def __str__(self):
        return repr(self.value)

class NoObservationError(TrayError):
    pass

class NoUndoError(TrayError):
    pass

class PropertyNotFoundError(TrayError):
    pass
    
class PropertyNotFoundError(TrayError):
    pass
    
class DoubleEmptyRecordError(TrayError):
    pass
    
class NoZipFileError(TrayError):
    pass

class BurnInBackgroundError(TrayError):
    pass