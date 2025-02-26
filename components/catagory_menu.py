import sys
from PyQt5.QtCore import Qt, pyqtSignal, QEasingCurve, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QApplication, QFrame, QWidget, QSizePolicy

from qfluentwidgets import (NavigationBar, NavigationItemPosition, NavigationWidget, MessageBox,
                            isDarkTheme, setTheme, Theme, setThemeColor, SearchLineEdit,
                            PopUpAniStackedWidget, getFont)
from qfluentwidgets import (FluentIcon as FIF, CardWidget, VBoxLayout,
                            TransparentTogglePushButton, TogglePushButton,
                            LineEdit, PrimaryToolButton, InfoBar, InfoBarPosition)

from qframelesswindow import FramelessWindow, TitleBar  

from components.database.crud import get_categories

class CatagoryWidget(CardWidget):

    categorySelected = pyqtSignal(str)

    def __init__(self, parent=None, categories = ["Data Analytics", "Computer Network", "Machine Learning", "Deep Learning", "Artificial Intelligence"]):
        super().__init__(parent)
        self.setFixedWidth(220)
        
        self.catagoryList = {}
        self.currentCheckedButton = None
        
        self.initUI(categories)

    def initUI(self, categories):
        self.base = VBoxLayout(self)

        self.allTag = TogglePushButton()
        self.allTag.setIcon(FIF.TAG)
        self.allTag.setChecked(True)
        self.currentCheckedButton = self.allTag
        self.allTag.setText("All Tasks")
        self.allTag.setObjectName("All Tasks")
        self.allTag.toggled.connect(lambda checked: self.selectOne(self.allTag, checked))
        self.base.addWidget(self.allTag)

        self.uncatagoryButton = TogglePushButton()
        self.uncatagoryButton.setIcon(FIF.UNPIN)
        self.uncatagoryButton.setText("Uncatagorised")
        self.uncatagoryButton.setObjectName("Uncatagorised")
        self.uncatagoryButton.toggled.connect(lambda checked: self.selectOne(self.uncatagoryButton, checked))
        self.base.addWidget(self.uncatagoryButton)

        if 'Uncatagorised' in categories:
            categories.remove('Uncatagorised')

        for category in categories:
            button = TransparentTogglePushButton()
            button.setText(category)
            button.setObjectName(category)
            button.toggled.connect(lambda checked, b=button: self.selectOne(b, checked))
            self.catagoryList[category] = button
            self.base.addWidget(button)

        addCategorySection = QHBoxLayout()
        self.addInput = LineEdit()
        addCatBtn = PrimaryToolButton()
        addCatBtn.setIcon(FIF.ADD)
        addCatBtn.clicked.connect(self.addCategory)

        addCategorySection.addWidget(self.addInput)
        addCategorySection.addWidget(addCatBtn)
        self.base.addLayout(addCategorySection)

        self.setLayout(self.base)
    
    def reloadWidget(self, categories):
        categories = get_categories()
        current_widgets = {self.base.itemAt(i).widget().objectName() for i in range(self.base.count()) if self.base.itemAt(i).widget()}
        for category in categories:
            if category not in current_widgets:
                button = TransparentTogglePushButton()
                button.setText(category)
                button.setObjectName(category)
                button.toggled.connect(lambda checked, b=button: self.selectOne(b, checked))
                self.catagoryList[category] = button
                self.base.insertWidget(self.base.count() - 1, button)

    def selectOne(self, selected_button, checked):
        if checked:
            if self.currentCheckedButton and self.currentCheckedButton != selected_button:
                self.currentCheckedButton.setChecked(False)
            self.currentCheckedButton = selected_button
            self.categorySelected.emit(selected_button.objectName())
        else:
            if self.currentCheckedButton == selected_button:
                self.currentCheckedButton = None

    def getSelectedCategory(self):
        if self.currentCheckedButton:
            return self.currentCheckedButton.objectName()
        else:
            return "All Tasks"

    def addCategory(self):
        new_category = self.addInput.text().strip()
        if new_category and new_category not in self.catagoryList:
            button = TransparentTogglePushButton()
            button.setText(new_category)
            button.setObjectName(new_category)
            button.toggled.connect(lambda checked, b=button: self.selectOne(b, checked))
            self.catagoryList[new_category] = button
            self.layout().insertWidget(self.layout().count() - 1, button)
            self.addInput.clear()
        else:
            InfoBar.warning(
                title='Lesson 3',
                content="Already Available",
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.BOTTOM,
                duration=2000,
                parent=self,
            )

class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        setTheme(Theme.DARK)

        # change the theme color
        # setThemeColor('#0078d4')

        self.initWindow()
        self.initUI()

    def initUI(self):
        catagoryWidget = CatagoryWidget()
        
        base = QVBoxLayout(self)
        base.setAlignment(Qt.AlignmentFlag.AlignTop)

        base.addWidget(catagoryWidget)

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