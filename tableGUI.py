import sys
from pathlib import Path

from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QSplashScreen
from sqlmodel import Session

from tableUI.const import BASE_DIR, DATA_PATH
from tableUI.db.initialise import init_db
from tableUI.gui import SenDTuiWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("SenDT UI")
    splash_pixmap = QPixmap(DATA_PATH / 'img' / 'splash.png')
    splash = QSplashScreen(splash_pixmap)
    splash.show()

    app.setWindowIcon(QIcon(splash_pixmap))

    print(Path(DATA_PATH / 'table_data.sqlite').absolute())

    engine = init_db(DATA_PATH / 'table_data.sqlite')

    with Session(engine) as session:
        app.setStyle('Fusion')
        window = SenDTuiWindow(session)
        window.show()
        splash.finish(window)
        sys.exit(app.exec())
