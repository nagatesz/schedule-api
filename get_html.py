import sys
from PyQt6.QtCore import QUrl, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView

class InspectorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login to flex.lkgeorge.org")
        self.resize(1000, 800)
        
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://flex.lkgeorge.org/student/schedule"))
        
        self.btn = QPushButton("Click here when you see your schedule fully loaded!")
        self.btn.clicked.connect(self.save_html)
        
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addWidget(self.btn)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def save_html(self):
        self.browser.page().toHtml(self.on_html)
        
    def on_html(self, html):
        with open("C:/Users/nagat/Downloads/SCHEDULEwidget/schedule.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("HTML saved successfully!")
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InspectorWindow()
    window.show()
    sys.exit(app.exec())
