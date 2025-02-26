from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from qfluentwidgets import (
    TitleLabel, SubtitleLabel, IconWidget, CardWidget, BodyLabel, CaptionLabel, SwitchButton, DropDownPushButton,
    ColorPickerButton, HyperlinkButton, isDarkTheme, setTheme, Theme, setThemeColor, RoundMenu, Action
)
from qfluentwidgets import FluentIcon as FIF
import sys


class VerticalSettingCard(CardWidget):
    def __init__(self, icon, title, content, parent=None, option=1):
        super().__init__(parent)
        self.iconWidget = IconWidget(icon)
        self.titleLabel = BodyLabel(title, self)
        self.contentLabel = CaptionLabel(content, self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(65)
        self.iconWidget.setFixedSize(20, 20)

        self.hBoxLayout.setContentsMargins(20, 11, 20, 11)
        self.hBoxLayout.setSpacing(15)
        self.hBoxLayout.addWidget(self.iconWidget)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignVCenter)
        self.vBoxLayout.addWidget(self.contentLabel, 0, Qt.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.hBoxLayout.addStretch(1)

        if option == 1:
            self.toggleButton = SwitchButton(self)
            self.hBoxLayout.addWidget(self.toggleButton, alignment=Qt.AlignRight)
        elif option == 2:
            self.menu = QWidget()
            self.themeButton = DropDownPushButton("Dark", self, FIF.CONSTRACT)

            # Menu actions for theme selection
            self.menu = RoundMenu(parent=self)
            self.menu.addAction(Action("Dark"))
            self.menu.addAction(Action("Light"))
            self.menu.addAction(Action("System"))
            self.themeButton.setMenu(self.menu)

            # Connect menu actions to theme-changing function
            self.menu.triggered.connect(self.changeTheme)
            self.hBoxLayout.addWidget(self.themeButton, alignment=Qt.AlignRight)
        elif option == 3:
            self.colorPickerButton = ColorPickerButton(QColor("#5012aaa2"), title="Color", parent=self)
            self.colorPickerButton.setFixedSize(32, 32)
            self.colorPickerButton.clicked.connect(self.changeThemeColor)
            self.hBoxLayout.addWidget(self.colorPickerButton, alignment=Qt.AlignRight)
        elif option == 4:
            self.linkButton = HyperlinkButton(
                url='https://contacts.google.com/person/c9172142090268153275',
                text='Documentation',
                parent=self,
                icon=FIF.LINK
            )
            self.hBoxLayout.addWidget(self.linkButton, alignment=Qt.AlignRight)
        elif option == 5:
            self.linkButton = HyperlinkButton(
                url='https://contacts.google.com/person/c9172142090268153275',
                text='Buy us a Coffee',
                parent=self,
                icon=FIF.CAFE
            )
            self.hBoxLayout.addWidget(self.linkButton, alignment=Qt.AlignRight)

    def changeThemeColor(self):
        setThemeColor(self.colorPickerButton.color)

    def changeTheme(self, action):
        """Update theme and apply globally with softer colors."""
        theme = action.text()
        self.themeButton.setText(theme)  # Update button text

        if theme == "Dark":
            setTheme(Theme.DARK)
            QApplication.instance().setStyleSheet("""
                QWidget {
                    background-color: #272727;
                    color: #dcdcdc;
                }
                QPushButton {
                    background-color: #3c3c3c;
                    color: #dcdcdc;
                }
                QLabel {
                    color: #dcdcdc;
                }
                /* Add other widget styles for dark theme here */
            """)
        elif theme == "Light":
            setTheme(Theme.LIGHT)
            QApplication.instance().setStyleSheet("""
                QWidget {
                    background-color: #f7f7f7; /* Off-white */
                    color: #2c2c2c; /* Dark gray */
                }
                QPushButton {
                    background-color: #e6e6e6; /* Light gray */
                    color: #2c2c2c;
                }
                QLabel {
                    color: #2c2c2c;
                }
                /* Add other widget styles for light theme here */
            """)
        elif theme == "System":
            setTheme(Theme.AUTO)
            QApplication.instance().setStyleSheet("")  # Reverts to default


class SettingsScreen(QWidget):
    def __init__(self):
        super().__init__()
        setTheme(Theme.DARK)

        self.vBoxLayout = QVBoxLayout(self)
        self.title1 = TitleLabel("Settings")
        self.title3 = SubtitleLabel("Personalisation")
        self.title2 = SubtitleLabel("About")

        self.vBoxLayout.addWidget(self.title1)
        self.vBoxLayout.addWidget(self.title3)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        self.vBoxLayout.addWidget(VerticalSettingCard(
            icon=FIF.TRANSPARENT,
            title="Mica effect",
            content="Apply semi transparent to windows and surfaces",
            option=1
        ))

        self.vBoxLayout.addWidget(VerticalSettingCard(
            icon=FIF.BRUSH,
            title="Application Theme",
            content="Change the appearance of your application",
            option=2
        ))

        self.vBoxLayout.addWidget(VerticalSettingCard(
            icon=FIF.PALETTE,
            title="Theme Color",
            content="Change the theme color of your application",
            option=3
        ))

        self.vBoxLayout.addWidget(self.title2)

        self.vBoxLayout.addWidget(VerticalSettingCard(
            icon=FIF.HELP,
            title="Help Center",
            content="Check out our documentation",
            option=4
        ))

        self.vBoxLayout.addWidget(VerticalSettingCard(
            icon=FIF.PEOPLE,
            title="Find Us",
            content="Get to know about the developers behind this project",
            option=5
        ))


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = SettingsScreen()
    w.show()
    app.exec_()
