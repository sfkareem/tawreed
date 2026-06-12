import sys
import asyncio
from PySide6.QtWidgets import QApplication
import qasync
from gui.main_window import MainWindow
from core import db

def main():
    # Initialize the database
    db.init_db()
    
    app = QApplication(sys.argv)
    
    # Initialize qasync Event Loop
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    window = MainWindow()
    window.show()
    
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()
