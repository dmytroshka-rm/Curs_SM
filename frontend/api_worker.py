from typing import Callable, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QThread


class ApiWorker(QObject):
    """
    Worker для виконання API-запитів у окремому потоці.
    """
    finished = pyqtSignal(object) 
    error = pyqtSignal(str) 

    def __init__(self, api_call: Callable[[], Any], parent: Optional[QObject] = None):
        super().__init__(parent)
        self.api_call = api_call

    def run(self):
        """Виконує API-запит у потоці."""
        try:
            result = self.api_call()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


