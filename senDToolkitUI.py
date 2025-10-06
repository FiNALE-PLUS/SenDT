import sys
from pathlib import Path

from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QSplashScreen
from sqlmodel import Session

from tableUI.const import DATA_PATH, FFMPEG_PATH
from tableUI.db.initialise import init_db
from tableUI.gui import SenDTuiWindow

if __name__ == '__main__':

    # TODO: Check if FFmpeg is in path if no local version is found
    if not FFMPEG_PATH.exists():
        raise EnvironmentError(f"No file is found at {FFMPEG_PATH}. \nPlease add an FFmpeg executable.")

    app = QApplication(sys.argv)
    app.setApplicationName("SenDT UI")
    splash_pixmap = QPixmap(DATA_PATH / 'img' / 'splash.png')
    splash = QSplashScreen(splash_pixmap)
    splash.show()

    app.setWindowIcon(QIcon(splash_pixmap))

    engine = init_db(DATA_PATH / 'table_data.sqlite')

    with Session(engine) as session:
        app.setStyle('Fusion')
        window = SenDTuiWindow(session)
        window.show()
        splash.finish(window)
        sys.exit(app.exec())
