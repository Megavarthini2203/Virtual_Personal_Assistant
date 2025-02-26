# coding:utf-8
import sys
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QAction, QVBoxLayout

from qfluentwidgets import (Dialog, setTheme, Theme, PrimaryPushButton, MessageDialog,
                            EditableComboBox, SubtitleLabel, MessageBoxBase, CaptionLabel, ComboBox,
                            LineEdit, TextEdit, CalendarPicker, TimePicker, InfoBadge, InfoLevel, TransparentPushButton)
from qfluentwidgets import FluentIcon as FIF
from datetime import datetime

from components.database.crud import (get_task_details, get_categories,
                                      update_category, update_task_description, update_task_title,
                                      update_task_status, update_task_due_date, update_task_priority,
                                      update_task_remainder_system)

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


class TaskEditDialog(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None, categories = ["Data Analysis", "Machine Learning", "Deep Learning"], task_id = ""):
        super().__init__(parent)

        print(task_id)

        categories = get_categories()
        categories.append('Uncatagorised')
        TASK = get_task_details(task_id)

        print(TASK)

        self.column = QHBoxLayout()

        self.doubleColumn1 = QVBoxLayout()

        self.titleLabel = SubtitleLabel('Task Summary (Editable)', self)

        self.statusLayout = QHBoxLayout()

        self.Status = InfoBadge(text=TASK.get("status", "Pending"), parent=self, level=InfoLevel.WARNING)
        self.timeLeft = TransparentPushButton(text = "2 Days Left")
        due_date_str = TASK.get("due_date", None)

        time_left_text = "No due date specified"

        if due_date_str:
            try:
                # Parse the due date
                from datetime import datetime
                print(due_date_str)
                if not isinstance(due_date_str, datetime):
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M")
                else:
                    due_date = due_date_str
                now = datetime.now()
                
                # Calculate time difference
                time_difference = due_date - now
                
                if time_difference.total_seconds() > 0:
                    # Format the time difference into days, hours, minutes
                    days = time_difference.days
                    hours, remainder = divmod(time_difference.seconds, 3600)
                    minutes, _ = divmod(remainder, 60)

                    # Construct the text
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
            except ValueError:
                time_left_text = "Invalid due date format"

        # Set the text to the TransparentPushButton
        self.timeLeft.setText(time_left_text)

        self.statusLayout.addWidget(self.Status, alignment=Qt.AlignmentFlag.AlignLeft)
        self.statusLayout.addWidget(self.timeLeft, alignment=Qt.AlignmentFlag.AlignRight)

        self.topLayout = QHBoxLayout()

        self.caption1 = CaptionLabel("Catagory", self)

        self.catagoryEditableCB = EditableComboBox(self)
        self.catagoryEditableCB.setPlaceholderText('Uncatagorised')
        self.catagoryEditableCB.addItems(categories)

        self.caption4 = CaptionLabel("Priority", self)
        self.priority = ComboBox(self)
        self.priority.addItems(["Low", "Medium", "High"])
        self.priority.setCurrentText(TASK.get("priority", "Medium"))

        self.topLayout.addWidget(self.caption1)
        self.topLayout.addWidget(self.catagoryEditableCB)
        self.topLayout.addWidget(self.caption4)
        self.topLayout.addWidget(self.priority)

        self.caption2 = CaptionLabel("Task Name", self)
        self.taskName = LineEdit(self)
        self.taskName.setText(TASK.get("title", ""))

        self.caption3 = CaptionLabel("Task Description", self)
        self.taskDescription = TextEdit(self)
        self.taskDescription.setText(TASK.get("description", ""))

        self.caption5 = CaptionLabel("Due", self)

        self.datetimeLayout = QHBoxLayout(self)

        self.datePicker = CalendarPicker(self)
        self.timePicker = TimePicker(self, showSeconds=True)

        # Set due date and time
        due_date = TASK.get("due_date", None)
        if due_date:
            from datetime import datetime
            if not isinstance(due_date, datetime):
                dt = datetime.strptime(due_date, "%Y-%m-%d %H:%M")
            else:
                dt = due_date
            self.datePicker.setDate(QDate(dt.year, dt.month, dt.day))
            self.timePicker.setTime(QTime(dt.hour, dt.minute))

        created_at = TASK.get("created_at", "")
        self.creationDateLabel = CaptionLabel(f"Task was created on {created_at}", self)

        self.datetimeLayout.addWidget(self.datePicker)
        self.datetimeLayout.addWidget(self.timePicker)

        self.doubleColumn1.addWidget(self.titleLabel)
        self.doubleColumn1.addLayout(self.statusLayout)
        self.doubleColumn1.addLayout(self.topLayout)

        self.doubleColumn1.addWidget(self.caption2)
        self.doubleColumn1.addWidget(self.taskName)
        self.doubleColumn1.addWidget(self.caption3)
        self.doubleColumn1.addWidget(self.taskDescription)

        self.doubleColumn1.addWidget(self.caption5)
        self.doubleColumn1.addLayout(self.datetimeLayout)
        self.doubleColumn1.addWidget(self.creationDateLabel)

        # Column 2
        self.doubleColumn2 = QVBoxLayout()

        # self.advancedCaption = SubtitleLabel("Advanced Options")

        # self.doubleColumn2.addWidget(self.advancedCaption)

        self.column.addLayout(self.doubleColumn1)
        self.column.addLayout(self.doubleColumn2)
        self.viewLayout.addLayout(self.column)

        self.yesButton.setText('Update')
        self.yesButton.clicked.connect(lambda: self.updateTaskDetails(TASK))
        self.cancelButton.setText('Cancel')

        # self.yesButton.setDisabled(True)

    def updateTaskDetails(self, TASK):

        current_date = self.datePicker.getDate().getDate()  # (year, month, day)
        current_time = self.timePicker.getTime()  # QTime object

        day, month, year = current_date[2], current_date[1], current_date[0]
        hour, minute = current_time.hour(), current_time.minute()

        now = datetime.now()
        current = now.strftime("%Y-%m-%d %H:%M")

        if (year, month, day) == (0, 0, 0):
            due_date = None
            status = "None"
        else:
            due_date = f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"

            due_datetime = datetime(year, month, day, hour, minute)
            
            status = "Pending" if due_datetime > now else "Overdue"

        modifiableTask = {
            "category": self.catagoryEditableCB.currentText(),
            "title": self.taskName.text(),
            "description": self.taskDescription.toPlainText(),
            "due_date": due_date,
            "priority": self.priority.text(),
            "status": status,
            "remainder_system": "Email",
            "modified_at": current,
            "is_human": True
        }

        if TASK['category'] is not modifiableTask['category']:
            update_category(TASK['_id'], modifiableTask['category'])

        if TASK['title'] is not modifiableTask['title']:
            update_task_title(TASK['_id'], modifiableTask['title'])
        
        if TASK['description'] is not modifiableTask['description']:
            update_task_description(TASK['_id'], modifiableTask['description'])

        if TASK['due_date'] is not modifiableTask['due_date']:
            update_task_due_date(TASK['_id'], modifiableTask['due_date'])
        
        if TASK['priority'] is not modifiableTask['priority']:
            update_task_priority(TASK['_id'], modifiableTask['priority'])
        
        if TASK['status'] is not modifiableTask['status']:
            update_task_status(TASK['_id'], modifiableTask['status'])
        
        if TASK['remainder_system'] is not modifiableTask['remainder_system']:
            update_task_remainder_system(TASK['_id'], modifiableTask['remainder_system'])

        print('Task details updated successfully')
            

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
        w = TaskEditDialog(self)
        
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