import os
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt


RESOURCE_DIR = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons')


def _fs_path(name: str) -> str:
    return os.path.join(RESOURCE_DIR, name)


def get_icon(name: str) -> QIcon:
    """Return a QIcon preferring a file in `frontend/resources/icons/`, otherwise try Qt resource paths."""
    # try filesystem first for easier local iteration
    fs = _fs_path(name)
    if os.path.exists(fs):
        return QIcon(fs)

    # try common resource prefixes used in this project
    for prefix in (":/icons/", ":/resources/icons/", ":/frontend/resources/icons/"):
        qpath = prefix + name
        ic = QIcon(qpath)
        if not ic.isNull():
            return ic

    # fallback empty
    return QIcon()


def get_pixmap(name: str, size: int = None) -> QPixmap:
    """Return a QPixmap from filesystem or resources. If size provided, scale preserving aspect."""
    fs = _fs_path(name)
    pm = QPixmap()
    if os.path.exists(fs):
        pm = QPixmap(fs)
    else:
        # try resource paths
        for prefix in (":/icons/", ":/resources/icons/", ":/frontend/resources/icons/"):
            qpath = prefix + name
            pm = QPixmap(qpath)
            if not pm.isNull():
                break

    if pm.isNull():
        return QPixmap()

    if size is not None:
        return pm.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return pm
