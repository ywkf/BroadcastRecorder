import sys
from PyQt6.QtCore import Qt, QDateTime, QDate, QEvent
from PyQt6.QtGui import QFont, QColor, QMouseEvent
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QLabel, QFrame, QSpacerItem, QSizePolicy, QScrollArea,
                             QListWidget, QListWidgetItem, QStackedWidget, QPushButton,
                             QLineEdit, QTableWidget, QTableWidgetItem, QComboBox,
                             QCalendarWidget, QDialog, QDialogButtonBox)


class TaskPage(QWidget):
    def __init__(self):
        super().__init__()
        self.reminders = []  # 存储提醒事项
        self.end_date = None
        self.init_ui()

    def init_ui(self):
        # 使用一个主框架实现圆角和边框
        main_frame = QFrame(self)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        main_layout.addWidget(main_frame)

        # 圆角、浅色边框、白色背景
        main_frame.setStyleSheet("""
            QFrame {
                background:white;
                border:1px solid #ccc;
                border-radius:10px;
            }
        """)
        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(20)

        # 显示日历
        self.calendar = QCalendarWidget(self)
        self.calendar.selectionChanged.connect(self.update_time_for_selected_date)
        # 为日历组件设置白底
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background:white; 
                border:1px solid #ccc; 
                border-radius:10px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background: white;
                selection-background-color: #cce0ff;
                selection-color: black;
                border-radius:5px;
            }
        """)
        frame_layout.addWidget(self.calendar)

        # 显示提醒事项表格
        self.reminder_table = QTableWidget(self)
        self.reminder_table.setRowCount(0)
        self.reminder_table.setColumnCount(3)
        self.reminder_table.setHorizontalHeaderLabels(["标题", "时间", "操作"])
        self.reminder_table.setColumnWidth(0, 250)
        self.reminder_table.setColumnWidth(1, 100)
        self.reminder_table.setColumnWidth(2, 150)
        self.reminder_table.setStyleSheet("""
            QTableWidget {
                background:white; 
                border:1px solid #ccc; 
                border-radius:10px;
                gridline-color:#ddd;
            }
            QHeaderView::section {
                background:white;
                border:none;
                font-weight:bold;
            }
        """)
        frame_layout.addWidget(self.reminder_table)

        # 添加提醒事项控件布局
        add_reminder_layout = QHBoxLayout()
        add_reminder_layout.setSpacing(10)

        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("请输入标题")
        self.title_input.setStyleSheet("""
            QLineEdit {
                background:white; 
                border:1px solid #ccc; 
                border-radius:5px; 
                padding:5px;
            }
        """)
        add_reminder_layout.addWidget(self.title_input)

        # 创建年份、月份、日期、时、分选择框
        def create_combo_box(items, default=None):
            cb = QComboBox()
            cb.addItems([str(i) for i in items])
            cb.setStyleSheet("""
                QComboBox {
                    background:white;
                    border:1px solid #ccc;
                    border-radius:5px;
                    padding:2px;
                }
                QComboBox QAbstractItemView {
                    background:white;
                    border:1px solid #ccc;
                    border-radius:5px;
                }
            """)
            if default is not None:
                cb.setCurrentText(str(default))
            return cb

        self.year_label = QLabel("年: ")
        self.year_input = create_combo_box(range(1900, 2101), 2024)

        self.month_label = QLabel("月: ")
        self.month_input = create_combo_box(range(1, 13), 12)

        self.day_label = QLabel("日: ")
        self.day_input = create_combo_box(range(1, 32), 15)

        self.hour_label = QLabel("时: ")
        self.hour_input = create_combo_box(range(0, 24), 12)

        self.minute_label = QLabel("分: ")
        self.minute_input = create_combo_box(range(0, 60), 30)

        # 重复选项
        self.repeat_label = QLabel("重复: ")
        self.repeat_checkbox = create_combo_box(["不重复", "每天", "每周", "每月", "每年"], "不重复")
        self.repeat_checkbox.currentIndexChanged.connect(self.toggle_end_date_visibility)

        # 结束日期按钮
        self.end_date_button = QPushButton("选择结束日期", self)
        self.end_date_button.setVisible(False)
        self.end_date_button.setStyleSheet("""
            QPushButton {
                background:white; 
                border:1px solid #ccc; 
                border-radius:5px; 
                padding:5px;
            }
            QPushButton:hover {
                background:#e7f1ff;
            }
        """)
        self.end_date_button.clicked.connect(self.open_end_date_calendar)

        # 添加按钮
        self.add_button = QPushButton("添加提醒", self)
        self.add_button.setStyleSheet("""
            QPushButton {
                background:#cce0ff; 
                border:1px solid #ccc; 
                border-radius:5px; 
                padding:5px;
            }
            QPushButton:hover {
                background:#b3d1ff;
            }
        """)
        self.add_button.clicked.connect(self.add_reminder)

        # 将各个控件添加到布局
        for w in [self.year_label, self.year_input, self.month_label, self.month_input,
                  self.day_label, self.day_input, self.hour_label, self.hour_input,
                  self.minute_label, self.minute_input, self.repeat_label, self.repeat_checkbox,
                  self.end_date_button, self.add_button]:
            add_reminder_layout.addWidget(w)

        frame_layout.addLayout(add_reminder_layout)

        # 默认显示今天的提醒事项
        self.update_reminders()

    def toggle_end_date_visibility(self):
        if self.repeat_checkbox.currentText() == "不重复":
            self.end_date_button.setVisible(False)
        else:
            self.end_date_button.setVisible(True)

    def update_time_for_selected_date(self):
        selected_date = self.calendar.selectedDate()
        current_time = QDateTime.currentDateTime()

        self.year_input.setCurrentText(str(selected_date.year()))
        self.month_input.setCurrentText(str(selected_date.month()))
        self.day_input.setCurrentText(str(selected_date.day()))
        self.hour_input.setCurrentText(str(current_time.time().hour()))
        self.minute_input.setCurrentText(str(current_time.time().minute()))

        self.update_reminders()

    def open_end_date_calendar(self):
        calendar_dialog = QDialog(self)
        calendar_dialog.setWindowTitle("选择结束日期")
        calendar_layout = QVBoxLayout(calendar_dialog)

        calendar_widget = QCalendarWidget(self)
        calendar_widget.setSelectionMode(QCalendarWidget.SelectionMode.SingleSelection)
        calendar_widget.setStyleSheet("""
            QCalendarWidget {
                background:white; 
                border:1px solid #ccc; 
                border-radius:10px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background: white;
                selection-background-color: #cce0ff;
                selection-color: black;
                border-radius:5px;
            }
        """)

        calendar_layout.addWidget(calendar_widget)

        never_button = QPushButton("永不", self)
        never_button.setStyleSheet("""
            QPushButton {
                background:white; 
                border:1px solid #ccc; 
                border-radius:5px; 
                padding:5px;
            }
            QPushButton:hover {
                background:#e7f1ff;
            }
        """)
        never_button.clicked.connect(lambda: self.set_end_date(None, calendar_dialog))

        select_button = QPushButton("选择", self)
        select_button.setStyleSheet("""
            QPushButton {
                background:#cce0ff; 
                border:1px solid #ccc; 
                border-radius:5px; 
                padding:5px;
            }
            QPushButton:hover {
                background:#b3d1ff;
            }
        """)
        select_button.clicked.connect(lambda: self.set_end_date(calendar_widget.selectedDate(), calendar_dialog))

        calendar_layout.addWidget(never_button)
        calendar_layout.addWidget(select_button)

        calendar_dialog.exec()

    def set_end_date(self, selected_date, dialog):
        if selected_date is None:
            self.end_date = "永不"
        else:
            self.end_date = selected_date.toString("yyyy-MM-dd")
        self.end_date_button.setText(f"结束日期: {self.end_date}")
        if dialog:
            dialog.accept()

    def add_reminder(self):
        title = self.title_input.text()
        year = int(self.year_input.currentText())
        month = int(self.month_input.currentText())
        day = int(self.day_input.currentText())
        hour = int(self.hour_input.currentText())
        minute = int(self.minute_input.currentText())

        remind_datetime = f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00"

        if title:
            reminder = {'title': title, 'remind_time': remind_datetime, 'repeat': False, 'end_date': self.end_date}
            repeat_option = self.repeat_checkbox.currentText()
            if repeat_option != "不重复":
                repeat_reminders = self.generate_repeat_reminders(
                    QDateTime.fromString(remind_datetime, "yyyy-MM-dd HH:mm:ss"), repeat_option)
                self.reminders.extend(repeat_reminders)
            else:
                self.reminders.append(reminder)
            self.title_input.clear()
            self.update_reminders()
        else:
            self.show_error_dialog("提醒事项标题不能为空")

    def generate_repeat_reminders(self, start_time, repeat_option):
        repeat_reminders = []
        current_time = start_time
        title = self.title_input.text()

        if self.end_date == "永不":
            self.end_date = QDateTime.currentDateTime().addYears(100).toString("yyyy-MM-dd")

        while current_time.toString("yyyy-MM-dd") <= self.end_date:
            repeat_reminders.append({
                'title': title,
                'remind_time': current_time.toString("yyyy-MM-dd HH:mm:ss"),
                'repeat': True,
                'end_date': self.end_date
            })

            if repeat_option == "每天":
                current_time = current_time.addDays(1)
            elif repeat_option == "每周":
                current_time = current_time.addDays(7)
            elif repeat_option == "每月":
                current_time = current_time.addMonths(1)
            elif repeat_option == "每年":
                current_time = current_time.addYears(1)

        return repeat_reminders

    def update_reminders(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.reminder_table.setRowCount(0)

        self.reminders.sort(key=lambda r: r['remind_time'])

        for reminder in self.reminders:
            if reminder['remind_time'].startswith(selected_date):
                remind_time = reminder['remind_time'].split()[1][:-3]
                row_position = self.reminder_table.rowCount()
                self.reminder_table.insertRow(row_position)
                self.reminder_table.setItem(row_position, 0, QTableWidgetItem(reminder['title']))
                self.reminder_table.setItem(row_position, 1, QTableWidgetItem(remind_time))

                self.reminder_table.item(row_position, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.reminder_table.item(row_position, 1).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                delete_button = QPushButton("删除", self)
                delete_button.setStyleSheet("""
                    QPushButton {
                        background:white; 
                        border:1px solid #ccc; 
                        border-radius:5px; 
                        padding:5px;
                    }
                    QPushButton:hover {
                        background:#e7f1ff;
                    }
                """)
                delete_button.clicked.connect(lambda _, row=row_position: self.confirm_delete_reminder(row))
                self.reminder_table.setCellWidget(row_position, 2, delete_button)

    def confirm_delete_reminder(self, row):
        confirmation_dialog = QDialog(self)
        confirmation_dialog.setWindowTitle("确认删除")
        confirmation_layout = QVBoxLayout()
        confirmation_layout.addWidget(QLabel("您确定要删除该提醒事项吗？"))

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No)
        confirmation_layout.addWidget(button_box)

        confirmation_dialog.setLayout(confirmation_layout)

        button_box.button(QDialogButtonBox.StandardButton.Yes).clicked.connect(
            lambda: self.delete_reminder(row, confirmation_dialog))
        button_box.button(QDialogButtonBox.StandardButton.No).clicked.connect(confirmation_dialog.reject)

        confirmation_dialog.exec()

    def delete_reminder(self, row, confirmation_dialog):
        reminder = self.reminders[row]
        if reminder['repeat']:
            # 删除所有同标题的重复提醒
            self.reminders = [r for r in self.reminders if r['title'] != reminder['title']]
        else:
            del self.reminders[row]
        self.update_reminders()
        confirmation_dialog.accept()

    def show_error_dialog(self, message):
        dialog = QDialog(self)
        dialog.setWindowTitle("错误")
        layout = QVBoxLayout()
        layout.addWidget(QLabel(message))
        dialog.setLayout(layout)
        dialog.exec()


class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        todo_frame = QFrame()
        todo_frame.setStyleSheet("""
            QFrame {
                background:white; 
                border:1px solid #ccc; 
                border-radius:10px;
            }
        """)
        todo_layout = QVBoxLayout(todo_frame)
        todo_layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("今日待办事项:")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)

        todo_list = QListWidget()
        todo_list.setStyleSheet("background:white; border:none;")
        todos = [("12:00", "任务1"), ("14:00", "任务2"), ("18:00", "任务3")]
        for t in todos:
            item = QListWidgetItem(f"{t[0]}    {t[1]}")
            item_font = QFont("Microsoft Yahei", 12)
            item.setFont(item_font)
            todo_list.addItem(item)

        todo_layout.addWidget(title_label)
        todo_layout.addWidget(todo_list)

        audio_frame = QWidget()
        audio_layout = QVBoxLayout(audio_frame)
        audio_layout.setSpacing(20)
        audio_layout.setContentsMargins(20, 20, 20, 20)
        audio_frame.setStyleSheet("background:white;")

        for i in range(1, 4):
            single_audio_frame = QFrame()
            single_audio_layout = QVBoxLayout(single_audio_frame)
            single_audio_layout.setSpacing(5)
            single_audio_frame.setStyleSheet("background:white;")

            audio_label = QLabel(f"音频 {i}")
            audio_label.setFont(QFont("Microsoft Yahei", 10, QFont.Weight.Bold))

            waveform_frame = QFrame()
            waveform_frame.setFrameShape(QFrame.Shape.Panel)
            waveform_frame.setFrameShadow(QFrame.Shadow.Raised)
            waveform_frame.setMinimumSize(200, 80)
            waveform_frame.setStyleSheet("""
                background:white; 
                border:1px solid #ccc; 
                border-radius:10px;
            """)

            single_audio_layout.addWidget(audio_label)
            single_audio_layout.addWidget(waveform_frame)
            audio_layout.addWidget(single_audio_frame)

        main_layout.addWidget(todo_frame)
        main_layout.addWidget(audio_frame)

        # 原比例为9:11
        main_layout.setStretch(0, 9)
        main_layout.setStretch(1, 11)


class DevicePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("设备页面示意")
        layout.addWidget(label)


class AudioDemoPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("音频页面示意")
        layout.addWidget(label)


class TextPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("文本页面示意")
        layout.addWidget(label)


class TaskSetPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("任务集页面示意")
        layout.addWidget(label)


class LogPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("日志页面示意")
        layout.addWidget(label)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MaaDxxw - 0.1.0")

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左侧导航栏
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        # 右侧内容区
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)

        # 添加页面
        self.create_pages()

        self.setCentralWidget(main_widget)
        self.resize(1000, 600)

    def create_sidebar(self):
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # 导航菜单
        nav_list = QListWidget()
        nav_list.setStyleSheet("""
            QListWidget {
                border:none; 
                background:white;
            }
            QListWidget::item {
                padding:10px; 
                border-bottom:1px solid #ddd;
            }
            QListWidget::item:hover {
                background:#e7f1ff; 
                border-radius:8px; 
                margin:3px;
            }
            QListWidget::item:selected {
                background:#cce0ff; 
                border-radius:8px; 
                margin:3px;
            }
        """)
        nav_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        main_menu = ["首页", "任务", "音频", "文本", "日志"]
        for item_text in main_menu:
            item = QListWidgetItem(item_text)
            nav_list.addItem(item)

        nav_list.setCurrentRow(0)
        nav_list.itemClicked.connect(self.on_nav_item_clicked)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background:white; border:none;")
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        nav_layout.addWidget(nav_list)
        nav_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        footer_menu = ["停止", "检查资源包", "检查更新", "设置", "关于"]
        for i, item_text in enumerate(footer_menu):
            footer_label = QLabel(item_text)
            footer_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            style = "padding:8px 12px; border-bottom:1px solid #ddd; background:white;"
            if i == 0:
                style = "padding:8px 12px; border-top:1px solid #ddd; border-bottom:1px solid #ddd; background:white;"
            footer_label.setStyleSheet(style)
            nav_layout.addWidget(footer_label)

        scroll_area.setWidget(nav_container)
        sidebar_layout.addWidget(scroll_area)

        sidebar_widget.setFixedWidth(200)
        return sidebar_widget

    def create_pages(self):
        # 首页页面
        page_home = HomePage()
        self.stack.addWidget(page_home)

        # 任务页面 - 使用整合后的TaskPage
        page_task = TaskPage()
        self.stack.addWidget(page_task)

        # 音频页面示意
        page_audio = AudioDemoPage()
        self.stack.addWidget(page_audio)

        # 文本页面示意
        page_text = TextPage()
        self.stack.addWidget(page_text)

        # 日志页面示意
        page_log = LogPage()
        self.stack.addWidget(page_log)

    def on_nav_item_clicked(self, item):
        text = item.text()
        mapping = {
            "首页": 0,
            "任务": 1,
            "音频": 2,
            "文本": 3,
            "日志": 4
        }
        if text in mapping:
            self.stack.setCurrentIndex(mapping[text])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
