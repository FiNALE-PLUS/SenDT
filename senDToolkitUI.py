import sys

from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QSplashScreen
from sqlmodel import Session

from const import DATA_PATH, FFMPEG_PATH
from db.initialise import init_local_db
from tableUI.gui import SenDTuiWindow
from tableUI.utils.settings.get_settings import get_sendt_settings

if __name__ == '__main__':
    # TODO: Check if FFmpeg is in path if no local version is found
    if not FFMPEG_PATH.exists():
        raise EnvironmentError(f"No file is found at: \n\t{FFMPEG_PATH}\nPlease add an FFmpeg executable.")

    # Use for settings file validation/creation
    _ = get_sendt_settings()

    app = QApplication(sys.argv)
    app.setApplicationName("SenDT UI")
    splash_pixmap = QPixmap(DATA_PATH / 'img' / 'splash.png')
    splash = QSplashScreen(splash_pixmap)
    splash.show()

    app.setWindowIcon(QIcon(splash_pixmap))

    engine = init_local_db(DATA_PATH / 'table_data.sqlite')

    with Session(engine) as session:

        app.setStyle('Fusion')
        window = SenDTuiWindow(session)
        window.show()
        splash.finish(window)
        sys.exit(app.exec())
