# coding:utf-8
import sys

from PyQt5.QtCore import Qt, pyqtSignal, QEasingCurve, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QApplication, QFrame, QWidget

from qfluentwidgets import (NavigationBar, NavigationItemPosition, NavigationWidget, MessageBox,
                            isDarkTheme, setTheme, Theme, setThemeColor, SearchLineEdit,
                            PopUpAniStackedWidget, getFont)
from qfluentwidgets import (FluentIcon as FIF, CardWidget, VBoxLayout,
                            PillPushButton, PrimaryPushButton, CheckBox,
                            TogglePushButton, InfoBadge, TransparentToolButton, CaptionLabel,
                            PrimaryToolButton, Dialog)

from qframelesswindow import FramelessWindow, TitleBar
from PyQt5.QtCore import pyqtSignal
from datetime import datetime

if __name__ == '__main__':
    from task_edit_dialog import TaskEditDialog
else:
    from components.task_edit_dialog import TaskEditDialog

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

class TaskWidget(CardWidget):
    taskDeleted = pyqtSignal(str)

    def __init__(self, parent=None, TASK=None, catagories=[]):
        super().__init__(parent)
        self.setFixedHeight(65)
        self.initUI(TASK, catagories)

        self.parent = parent
        self.task_id = str(TASK['_id'])

    def initUI(self, TASK, catagories):
        
        base = QHBoxLayout()
        base.setContentsMargins(20, 0, 20, 0)

        self.checkBox = CheckBox(TASK['title'], self)
        self.checkBox.setTristate(True)

        self.catagoryBadge = PillPushButton(TASK['category'])
        self.catagoryBadge.setIcon(FIF.TAG)
        self.catagoryBadge.setChecked(True)

        # self.catagoryBadge.setFixedWidth(len(TASK['category'])*10)

        self.moreOptions = TransparentToolButton(FIF.MORE)
        self.moreOptions.clicked.connect(self.open_create_dialog)

        due_date = TASK['due_date']

        if due_date is not None:

            if type(due_date) == type("str"):
                due_date = datetime.strptime(due_date, "%Y-%m-%d %H:%M")

            now = datetime.now()
            
            time_difference = due_date - now
            
            if time_difference.total_seconds() > 0:
                days = time_difference.days
                hours, remainder = divmod(time_difference.seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                if days > 0:
                    time_left_text = f"{days} Days Left"
                elif hours > 0:
                    time_left_text = f"{hours} Hours Left"
                elif minutes > 0:
                    time_left_text = f"{minutes} Minutes Left"
                else:
                    time_left_text = "Less than a minute left"
            else:
                time_left_text = "Past Due"
        else:
            time_left_text = "Past Due"

        self.dueTime = CaptionLabel(time_left_text)

        self.delete_button  = PrimaryToolButton(FIF.DELETE)
        self.delete_button.clicked.connect(self.deleteDialog)

        base.addWidget(self.checkBox)
        base.addWidget(self.dueTime, alignment=Qt.AlignmentFlag.AlignRight)
        base.addWidget(self.catagoryBadge, alignment=Qt.AlignmentFlag.AlignRight)
        base.addWidget(self.moreOptions)
        base.addWidget(self.delete_button)

        self.setLayout(base)

    def open_create_dialog(self):

        cdialog = TaskEditDialog(self.parent, task_id=self.task_id)
        if cdialog.exec():
            print('Yes button is pressed')
        else:
            print('Cancel button is pressed')

    def deleteDialog(self):
        title = 'Are you sure?'
        content = """This action cannot be undone!"""
        w = Dialog(title, content)
        w.setTitleBarVisible(False)
        if w.exec():
            self.taskDeleted.emit(self.task_id)  # Emit signal when deleting the task.
            self.close()
            print('Yes button is pressed')
        else:
            print('Cancel button is pressed')

class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        setTheme(Theme.DARK)

        # change the theme color
        # setThemeColor('#0078d4')

        self.initWindow()
        self.initUI()

    def initUI(self):
        taskWidget = TaskWidget(self, TASK='Sample', catagories=['sample'])
        
        base = VBoxLayout(self)

        base.setContentsMargins(10, 100, 10, 10)

        base.addWidget(taskWidget)

        self.setLayout(base)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('ToDoBot')
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        self.setQss()

    def setQss(self):
        color = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/{color}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec_()