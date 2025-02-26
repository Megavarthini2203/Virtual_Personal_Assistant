# coding:utf-8
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QAction, QVBoxLayout

from qfluentwidgets import (Dialog, setTheme, Theme, PrimaryPushButton, MessageDialog,
                            EditableComboBox, SubtitleLabel, MessageBoxBase, CaptionLabel, ComboBox,
                            LineEdit, TextEdit, CalendarPicker, TimePicker)
from qfluentwidgets import FluentIcon as FIF
import datetime
from PyQt5.QtCore import QDateTime
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


class TaskDialog(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None, categories = ["Data Analysis", "Machine Learning", "Deep Learning"]):
        super().__init__(parent=parent)

        self.column = QHBoxLayout()

        self.doubleColumn1 = QVBoxLayout()

        self.titleLabel = SubtitleLabel('Create a new Task', self)

        self.topLayout = QHBoxLayout()

        self.caption1 = CaptionLabel("Catagory", self)

        self.catagoryEditableCB = EditableComboBox(self)
        self.catagoryEditableCB.setPlaceholderText('Uncatagorised')
        self.catagoryEditableCB.addItems(categories)
        self.catagoryEditableCB.setText("Uncatagorised")

        self.caption4 = CaptionLabel("Priority", self)
        self.priority = ComboBox(self)
        self.priority.addItems(["Low", "Medium", "High"])

        self.topLayout.addWidget(self.caption1)
        self.topLayout.addWidget(self.catagoryEditableCB)
        self.topLayout.addWidget(self.caption4)
        self.topLayout.addWidget(self.priority)

        self.caption2 = CaptionLabel("Enter Task Name (More than 3 chars)", self)
        self.taskName = LineEdit(self)
        self.taskName.textChanged.connect(self.enableTaskCreation)

        self.caption3 = CaptionLabel("Enter Task Description", self)
        self.taskDescription = TextEdit(self)

        self.caption5 = CaptionLabel("Select Due", self)

        self.datetimeLayout = QHBoxLayout()

        self.datePicker = CalendarPicker(self)
        self.timePicker = TimePicker(self, showSeconds=True)

        self.datetimeLayout.addWidget(self.datePicker)
        self.datetimeLayout.addWidget(self.timePicker)

        self.doubleColumn1.addWidget(self.titleLabel)
        self.doubleColumn1.addLayout(self.topLayout)

        self.doubleColumn1.addWidget(self.caption2)
        self.doubleColumn1.addWidget(self.taskName)
        self.doubleColumn1.addWidget(self.caption3)
        self.doubleColumn1.addWidget(self.taskDescription)

        self.doubleColumn1.addWidget(self.caption5)
        self.doubleColumn1.addLayout(self.datetimeLayout)

        # Column 2
        self.doubleColumn2 = QVBoxLayout()

        # self.advancedCaption = SubtitleLabel("Advanced Options")

        # self.doubleColumn2.addWidget(self.advancedCaption)

        self.column.addLayout(self.doubleColumn1)
        self.column.addLayout(self.doubleColumn2)
        self.viewLayout.addLayout(self.column)

        self.yesButton.setText('Create')
        self.cancelButton.setText('Cancel')

        self.yesButton.setDisabled(True)

    def enableTaskCreation(self):
        taskName = self.taskName.text()

        if len(taskName) > 3:
            self.yesButton.setDisabled(False)
        else:
            self.yesButton.setDisabled(True)

    def getTaskDetails(self):
        current_date = self.datePicker.getDate().getDate()  # (year, month, day)
        current_time = self.timePicker.getTime()  # QTime object

        day, month, year = current_date[2], current_date[1], current_date[0]
        hour, minute = current_time.hour(), current_time.minute()

        now = datetime.datetime.now()

        if (year, month, day) == (0, 0, 0):
            due_date = None
            status = "None"
        else:
            due_date = f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"

            due_datetime = datetime.datetime(year, month, day, hour, minute)
            
            status = "Pending" if due_datetime > now else "Overdue"

        current = now.strftime("%Y-%m-%d %H:%M")

        task = {
            "category": self.catagoryEditableCB.currentText(),
            "title": self.taskName.text(),
            "description": self.taskDescription.toPlainText(),
            "due_date": due_date,
            "priority": self.priority.text(),
            "status": status,
            "created_at": current,
            "remainder_system": "Email",
            "modified_at": current,
            "is_human": True
        }

        return task

class Demo(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.resize(950, 500)
        self.btn = PrimaryPushButton('Click Me', parent=self)
        self.btn.move(425, 225)
        self.btn.clicked.connect(self.showDialog)
        self.setStyleSheet('Demo{background:white}')

        setTheme(Theme.DARK)

    def showDialog(self):
        w = TaskDialog(self)
        
        if w.exec():
            print('Yes button is pressed')
        else:
            print('Cancel button is pressed')


if __name__ == '__main__':
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = Demo()
    w.show()
    sys.exit(app.exec_())