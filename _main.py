# coding:utf-8
import sys
import subprocess
import os
import time as time2
from time import sleep, time

from PyQt5.QtCore import Qt, pyqtSignal, QEasingCurve, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QApplication, QFrame, QWidget, QScrollArea

from qfluentwidgets import (NavigationBar, NavigationItemPosition, NavigationWidget, MessageBox,
                            isDarkTheme, setTheme, Theme, setThemeColor, SearchLineEdit, CardWidget, ImageLabel, ProgressRing,
                            PopUpAniStackedWidget, getFont, PrimaryPushButton, SubtitleLabel, SmoothScrollArea, VBoxLayout)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, TitleBar
from components.todo_widget import TaskWidget
from components.catagory_menu import CatagoryWidget
from components.task_dialog import TaskDialog
from components.task_edit_dialog import TaskEditDialog
from components.settings import SettingsScreen
from components.database.crud import (get_all_tasks, get_categories, get_all_tasks_by_category,
                           add_task_with_dictionary, delete_task)
from brain.cerebrum import mark_relavance_and_process,process_updates


'''
Task Fields: category, title, description, due_date, priority, status, created_at, remainder_system, modified_at, is_human

Task Category: Work
Task Title: Review code changes
Task Description: Check for errors and potential improvements in the code.
Task Due Date: 2024-10-24 14:00:00
Task Priority: Medium
Task Status: Pending
Task Created At: 2024-10-22 15:00:00
Task Modified At: 2024-10-22 16:00:00
Task Remainder System: Email
Task Is Human: True
'''

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from PyQt5.QtCore import QThread, pyqtSignal
from qfluentwidgets import setTheme, Theme
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('mongodb://localhost:27017/')

db = client['whatsapp']
collection = db['messages']

class DocumentMonitorThread(QThread):
    new_document_detected = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        last_checked_id = None
        print("Monitoring MongoDB for new documents...")

        while self.running:
            try:
                # Fetch documents inserted after the last checked document
                query = {"_id": {"$gt": ObjectId(last_checked_id)}} if last_checked_id else {}
                new_docs = collection.find(query).sort("_id")
                
                for doc in new_docs:
                    print("New document detected:", doc)
                    last_checked_id = str(doc["_id"])
                    mark_relavance_and_process()
                    self.new_document_detected.emit()
                process_updates()   
                time2.sleep(2)  # Polling interval

            except Exception as e:
                print("Error during monitoring:", e)
                time2.sleep(5)

    def stop(self):
        self.running = False

from qfluentwidgets import SmoothScrollArea, PixmapLabel
from PyQt5.QtGui import QPixmap

class ScrollWidget(SmoothScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.setScrollAnimation(Qt.Vertical, 400, QEasingCurve.OutQuint)
        self.resize(1200, 800)
        with open('resource/dark/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
        setTheme(Theme.DARK)

class Widget(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.setObjectName(text.replace(' ', '-'))

        self.contentSplit = QHBoxLayout()
        self.catagoryLayout = QVBoxLayout()
        
        scrollWidget = ScrollWidget(self)
        scrollContent = QWidget()

        self.listLayout = VBoxLayout(scrollContent)
        scrollWidget.setWidget(scrollContent)
        scrollWidget.setWidgetResizable(True)

        setTheme(Theme.DARK)
        
        self.contentSplit.addLayout(self.catagoryLayout, stretch=1)
        self.contentSplit.addWidget(scrollWidget, stretch=4)

        self.settingsTile = QVBoxLayout()
        self.connectLayout = QVBoxLayout()

        if text == "Home":
            self.__init_home()
            self.setLayout(self.contentSplit)
            self.monitor_thread = DocumentMonitorThread()
            self.monitor_thread.new_document_detected.connect(self.change_task_list_category)
            self.monitor_thread.start()
        elif text == "Settings":
            self._init_settings()
            self.setLayout(self.settingsTile)
        elif text == "Connect":
            self._init_connect()
            self.setLayout(self.connectLayout)

    def closeEvent(self, event):
        self.monitor_thread.stop()
        self.monitor_thread.wait()
        super().closeEvent(event)

    def _init_connect(self):
        self.title = SubtitleLabel("Connect To WhatsApp")

        self.generateQRButton = PrimaryPushButton("Generate QR Code", icon = FIF.QRCODE)
        self.generateQRButton.clicked.connect(self.on_generate_qr)

        self.connectLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.connectLayout.addWidget(self.title)
        self.connectLayout.addWidget(self.generateQRButton)

    def on_generate_qr(self):
        js_file = "test.js"
        qr_code_path = "qr-code.png"
        place_holder_path = "qr-code-place-holder.png"
        timeout = 10

        try:
            subprocess.Popen(["node", js_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("JavaScript process started independently.")
        except FileNotFoundError:
            print("Node.js is not installed or not found in PATH.")
            return
        except Exception as e:
            print(f"An error occurred: {e}")
            return

        start_time = time()
        while not os.path.exists(qr_code_path):
            if time() - start_time > timeout:
                print("Timeout reached. QR code generation took too long.")
                break
            print("Waiting for QR code to be generated...")
            sleep(0.5)

        if not hasattr(self, 'qrCode'):
            if os.path.exists(qr_code_path):
                self.qrCode = ImageLabel(qr_code_path)
                print("QR code found and loaded.")
            else:
                self.qrCode = ImageLabel(place_holder_path)
                print("Using placeholder for QR code.")

            self.qrCode.scaledToHeight(512)
            self.qrCode.setMargin(10)
            self.connectLayout.addWidget(self.qrCode)
            print("QR Code widget added.")

    def _init_settings(self):
        self.settings = SettingsScreen()
        self.settingsTile.addWidget(self.settings)

    def __init_home(self):

        mark_relavance_and_process()

        self.addTaskHomeButton = PrimaryPushButton("Compose Task", icon = FIF.DICTIONARY_ADD)
        # self.addTaskHomeButton.setFixedWidth(300)
        self.addTaskHomeButton.setFixedHeight(65)
        self.addTaskHomeButton.clicked.connect(self.on_add_task_home_clicked)

        self.catagoryLayout.addWidget(self.addTaskHomeButton)

        tasks = get_all_tasks()

        self.categoryLabel = SubtitleLabel("   All Tasks")

        # self.listLayout.addStretch(1)  # Add spacer to fill the remaining space
        self.listLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.listLayout.addWidget(self.categoryLabel)

        self.categoryWidget = CatagoryWidget(parent=self, categories=get_categories())
        self.categoryWidget.categorySelected.connect(self.change_task_list_category)

        for task in tasks:
            taskWidget = TaskWidget(parent=self, TASK=task)
            taskWidget.setObjectName(str(task['_id']))
            taskWidget.taskDeleted.connect(self.delete_task_widget)
            self.listLayout.addWidget(taskWidget)

        self.catagoryLayout.addWidget(self.categoryWidget, alignment=Qt.AlignmentFlag.AlignTop, stretch=1)

    def delete_task_widget(self, task_id):
        """Handle task widget deletion."""
        for i in range(self.listLayout.count()):
            item = self.listLayout.itemAt(i)
            widget = item.widget()
            if widget and widget.objectName() == task_id:
                widget.deleteLater()
                delete_task(task_id=task_id)
                print(f'Task with ID {task_id} deleted.')
                break

    def change_task_list_category(self):
        if not hasattr(self, 'categoryWidget') or self.categoryWidget is None:
            return

        for i in reversed(range(1, self.listLayout.count())):
            item = self.listLayout.takeAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        category = self.categoryWidget.getSelectedCategory()
        self.categoryLabel.setText(f"   {category}")

        if category == 'All Tasks':
            tasks = get_all_tasks()
        else:
            tasks = get_all_tasks_by_category(category)

        for task in tasks:
            taskWidget = TaskWidget(parent=self, TASK=task, catagories=get_categories())
            taskWidget.setObjectName(str(task['_id']))
            taskWidget.taskDeleted.connect(self.delete_task_widget)
            self.listLayout.addWidget(taskWidget)

    def clear_layout(self):
        while self.listLayout.count() > 0:
            item = self.listLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def on_add_task_home_clicked(self):
        categories = get_categories()
        w = TaskDialog(self.parent, categories)

        if w.exec():
            task = w.getTaskDetails()
            add_task_with_dictionary(task)

            taskWidget = TaskWidget(parent=self, TASK=task, catagories=categories)
            taskWidget.setObjectName(str(task['_id']))
            self.listLayout.addWidget(taskWidget)

            self.categoryWidget.reloadWidget(categories=categories)

            print('Yes button is pressed')
        else:
            print('Cancel button is pressed')

class StackedWidget(QFrame):
    """ Stacked widget """

    currentChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.view = PopUpAniStackedWidget(self)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.view)

        self.view.currentChanged.connect(self.currentChanged)

    def addWidget(self, widget):
        """ add widget to view """
        self.view.addWidget(widget)

    def widget(self, index: int):
        return self.view.widget(index)

    def setCurrentWidget(self, widget, popOut=False):
        if not popOut:
            self.view.setCurrentWidget(widget, duration=300)
        else:
            self.view.setCurrentWidget(
                widget, True, False, 200, QEasingCurve.InQuad)

    def setCurrentIndex(self, index, popOut=False):
        self.setCurrentWidget(self.view.widget(index), popOut)


class CustomTitleBar(TitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.hBoxLayout.removeWidget(self.minBtn)
        self.hBoxLayout.removeWidget(self.maxBtn)
        self.hBoxLayout.removeWidget(self.closeBtn)

        # add window icon
        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(18, 18)
        self.hBoxLayout.insertSpacing(0, 20)
        self.hBoxLayout.insertWidget(
            1, self.iconLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self.window().windowIconChanged.connect(self.setIcon)

        # add title label
        self.titleLabel = QLabel(self)
        self.titleLabel.setText("ToDoBoT")
        self.hBoxLayout.insertWidget(
            2, self.titleLabel, 0, Qt.AlignLeft | Qt.AlignVCenter)
        self.titleLabel.setObjectName('titleLabel')
        self.window().windowTitleChanged.connect(self.setTitle)

        # add search line edit
        self.searchLineEdit = SearchLineEdit(self)
        self.searchLineEdit.setPlaceholderText('Search Anything...')
        self.searchLineEdit.setFixedWidth(400)
        self.searchLineEdit.setClearButtonEnabled(True)

        self.vBoxLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(0)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.setAlignment(Qt.AlignTop)
        self.buttonLayout.addWidget(self.minBtn)
        self.buttonLayout.addWidget(self.maxBtn)
        self.buttonLayout.addWidget(self.closeBtn)
        self.vBoxLayout.addLayout(self.buttonLayout)
        self.vBoxLayout.addStretch(1)
        self.hBoxLayout.addLayout(self.vBoxLayout, 0)

    def setTitle(self, title):
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setIcon(self, icon):
        self.iconLabel.setPixmap(QIcon(icon).pixmap(18, 18))

    def resizeEvent(self, e):
        self.searchLineEdit.move((self.width() - self.searchLineEdit.width()) //2, 8)

class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))

        # use dark theme mode
        setTheme(Theme.DARK)

        # change the theme color
        # setThemeColor('#0078d4')

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationBar = NavigationBar(self)
        self.stackWidget = StackedWidget(self)

        # create sub interface
        self.homeInterface = Widget('Home', self)
        self.appInterface = Widget('Documents', self)
        self.videoInterface = Widget('Connect', self)
        self.libraryInterface = Widget('Settings', self)

        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 48, 0, 0)
        self.hBoxLayout.addWidget(self.navigationBar)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, 'Home', selectedIcon=FIF.HOME_FILL)
        self.addSubInterface(self.appInterface, FIF.MEDIA, 'Media')
        self.addSubInterface(self.videoInterface, FIF.QRCODE, 'Connect')

        self.addSubInterface(self.libraryInterface, FIF.SETTING, 'Setting', NavigationItemPosition.BOTTOM, FIF.SETTING)
        self.navigationBar.addItem(
            routeKey='Help',
            icon=FIF.HELP,
            text='Help',
            onClick=self.showMessageBox,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.navigationBar.setCurrentItem(self.homeInterface.objectName())

        # hide the text of button when selected
        self.navigationBar.setSelectedTextVisible(False)

        # adjust the font size of button
        self.navigationBar.setFont(getFont(12))

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('ToDoBot')
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        self.setQss()

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP, selectedIcon=None):
        """ add sub interface """
        self.stackWidget.addWidget(interface)
        self.navigationBar.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            selectedIcon=selectedIcon,
            position=position,
        )

    def setQss(self):
        color = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/{color}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationBar.setCurrentItem(widget.objectName())

    def showMessageBox(self):
        w = MessageBox(
            'All hail Rameez',
            'To learn more about Oogway Rameez, please visit his github',
            self
        )
        w.yesButton.setText('GitHub')
        w.cancelButton.setText('Nah')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://github.com/RameezAkther"))


if __name__ == '__main__':

    file_path = "qr-code.png"

    if os.path.exists(file_path):
        os.remove(file_path)
        print("File deleted.")
    else:
        print("File not found.")

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec_()
