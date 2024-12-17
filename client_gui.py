import sys
from PyQt6.QtCore import Qt, QDateTime, QDate
from PyQt6.QtGui import QIcon, QMouseEvent
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTableWidget, \
    QTableWidgetItem, QComboBox, QLabel, QCalendarWidget, QDialog, QDialogButtonBox, QDateEdit, QDialog


class ReminderApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("提醒事项")
        self.setWindowIcon(QIcon("reminder_icon.png"))
        self.setGeometry(100, 100, 1200, 800)  # 增大窗口大小

        self.reminders = []  # 存储提醒事项

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 显示日历
        self.calendar = QCalendarWidget(self)
        self.calendar.selectionChanged.connect(self.update_time_for_selected_date)
        layout.addWidget(self.calendar)

        # 显示今天的提醒事项
        self.reminder_table = QTableWidget(self)
        self.reminder_table.setRowCount(0)  # 不再固定行数，初始为0
        self.reminder_table.setColumnCount(3)  # 列数：标题、时间、操作
        self.reminder_table.setHorizontalHeaderLabels(["标题", "时间", "操作"])

        # 调整事项列表的列宽度
        self.reminder_table.setColumnWidth(0, 250)  # 设置标题列宽度
        self.reminder_table.setColumnWidth(1, 100)  # 设置时间列宽度
        self.reminder_table.setColumnWidth(2, 150)  # 设置操作列宽度

        layout.addWidget(self.reminder_table)

        # 添加提醒事项控件
        add_reminder_layout = QHBoxLayout()
        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("请输入标题")
        add_reminder_layout.addWidget(self.title_input)

        # 年、月、日、小时、分钟选择控件
        self.year_label = QLabel("年: ", self)
        self.year_input = QComboBox(self)
        self.year_input.addItems([str(year) for year in range(1900, 2101)])  # 年份范围
        self.year_input.setCurrentText("2024")  # 默认年份
        add_reminder_layout.addWidget(self.year_label)
        add_reminder_layout.addWidget(self.year_input)

        # 月选择框
        self.month_label = QLabel("月: ", self)
        self.month_input = QComboBox(self)
        self.month_input.addItems([str(month) for month in range(1, 13)])  # 月份范围
        self.month_input.setCurrentText("12")  # 默认月份
        add_reminder_layout.addWidget(self.month_label)
        add_reminder_layout.addWidget(self.month_input)

        # 日选择框
        self.day_label = QLabel("日: ", self)
        self.day_input = QComboBox(self)
        self.day_input.addItems([str(day) for day in range(1, 32)])  # 日范围
        self.day_input.setCurrentText("15")  # 默认日
        add_reminder_layout.addWidget(self.day_label)
        add_reminder_layout.addWidget(self.day_input)

        # 时选择框
        self.hour_label = QLabel("时: ", self)
        self.hour_input = QComboBox(self)
        self.hour_input.addItems([str(hour) for hour in range(0, 24)])  # 小时范围
        self.hour_input.setCurrentText("12")  # 默认时
        add_reminder_layout.addWidget(self.hour_label)
        add_reminder_layout.addWidget(self.hour_input)

        # 分选择框
        self.minute_label = QLabel("分: ", self)
        self.minute_input = QComboBox(self)
        self.minute_input.addItems([str(minute) for minute in range(0, 60)])  # 分钟范围
        self.minute_input.setCurrentText("30")  # 默认分
        add_reminder_layout.addWidget(self.minute_label)
        add_reminder_layout.addWidget(self.minute_input)

        # 重复选项
        self.repeat_label = QLabel("重复: ", self)
        self.repeat_checkbox = QComboBox(self)
        self.repeat_checkbox.addItems(["不重复", "每天", "每周", "每月", "每年"])
        self.repeat_checkbox.setCurrentText("不重复")
        self.repeat_checkbox.currentIndexChanged.connect(self.toggle_end_date_visibility)  # 添加信号连接
        add_reminder_layout.addWidget(self.repeat_label)
        add_reminder_layout.addWidget(self.repeat_checkbox)

        # 结束日期按钮
        self.end_date_button = QPushButton("选择结束日期", self)
        self.end_date_button.clicked.connect(self.open_end_date_calendar)
        self.end_date_button.setVisible(False)  # 默认隐藏
        add_reminder_layout.addWidget(self.end_date_button)

        self.end_date = None  # 初始化结束日期为空

        # 添加按钮
        self.add_button = QPushButton("添加提醒", self)
        self.add_button.clicked.connect(self.add_reminder)
        add_reminder_layout.addWidget(self.add_button)

        layout.addLayout(add_reminder_layout)

        self.setLayout(layout)

        # 默认显示今天的提醒事项
        self.update_reminders()

    def toggle_end_date_visibility(self):
        # 根据重复选项，显示或隐藏结束日期按钮
        if self.repeat_checkbox.currentText() == "不重复":
            self.end_date_button.setVisible(False)
        else:
            self.end_date_button.setVisible(True)

    def update_time_for_selected_date(self):
        # 获取当前选中的日期
        selected_date = self.calendar.selectedDate()

        # 获取当前时间
        current_time = QDateTime.currentDateTime()

        # 设置时、分为当前时间
        self.year_input.setCurrentText(str(selected_date.year()))
        self.month_input.setCurrentText(str(selected_date.month()))
        self.day_input.setCurrentText(str(selected_date.day()))
        self.hour_input.setCurrentText(str(current_time.time().hour()))
        self.minute_input.setCurrentText(str(current_time.time().minute()))

        # 更新显示的提醒事项
        self.update_reminders()

    def open_end_date_calendar(self):
        # 打开结束日期的选择窗口
        calendar_dialog = QDialog(self)
        calendar_dialog.setWindowTitle("选择结束日期")

        calendar_layout = QVBoxLayout()
        calendar_widget = QCalendarWidget(self)
        calendar_widget.setSelectionMode(QCalendarWidget.SelectionMode.SingleSelection)
        calendar_widget.selectionChanged.connect(self.on_date_selected)

        # 设置双击选择
        calendar_widget.mouseDoubleClickEvent = self.on_calendar_double_click

        calendar_layout.addWidget(calendar_widget)

        # 永不选项
        never_button = QPushButton("永不", self)
        never_button.clicked.connect(lambda: self.set_end_date(None, calendar_dialog))

        # 确认选择
        select_button = QPushButton("选择", self)
        select_button.clicked.connect(lambda: self.set_end_date(calendar_widget.selectedDate(), calendar_dialog))

        calendar_layout.addWidget(never_button)
        calendar_layout.addWidget(select_button)

        calendar_dialog.setLayout(calendar_layout)
        calendar_dialog.exec()

    def on_calendar_double_click(self, event: QMouseEvent):
        # 捕捉双击事件，选择日期
        selected_date = self.calendar.selectedDate()
        self.set_end_date(selected_date, None)  # 双击日期选择结束日期
        self.calendar.parent().close()  # 关闭日历窗口

    def on_date_selected(self):
        selected_date = self.calendar.selectedDate()
        self.set_end_date(selected_date, None)  # 选择结束日期

    def set_end_date(self, selected_date, dialog):
        # 设置结束日期
        if selected_date is None:
            self.end_date = "永不"
        else:
            self.end_date = selected_date.toString("yyyy-MM-dd")

        self.end_date_button.setText(f"结束日期: {self.end_date}")
        if dialog:
            dialog.accept()

    def add_reminder(self):
        # 获取输入的提醒事项
        title = self.title_input.text()
        year = int(self.year_input.currentText())
        month = int(self.month_input.currentText())
        day = int(self.day_input.currentText())
        hour = int(self.hour_input.currentText())
        minute = int(self.minute_input.currentText())

        remind_datetime = f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00"  # 格式化日期时间

        if title:
            # 创建提醒事项字典
            reminder = {'title': title, 'remind_time': remind_datetime, 'repeat': False, 'end_date': self.end_date}

            # 如果是重复事项
            repeat_option = self.repeat_checkbox.currentText()
            if repeat_option != "不重复":
                repeat_reminders = self.generate_repeat_reminders(QDateTime.fromString(remind_datetime, "yyyy-MM-dd HH:mm:ss"), repeat_option)
                self.reminders.extend(repeat_reminders)
            else:
                self.reminders.append(reminder)

            self.title_input.clear()
            self.update_reminders()
        else:
            self.show_error_dialog("提醒事项标题不能为空")

    def generate_repeat_reminders(self, start_time, repeat_option):
        # 生成重复事项
        repeat_reminders = []
        current_time = start_time

        # 获取用户输入的标题
        title = self.title_input.text()

        if self.end_date == "永不":
            self.end_date = QDateTime.currentDateTime().addYears(100).toString("yyyy-MM-dd")

        while current_time.toString("yyyy-MM-dd") <= self.end_date:
            # 使用用户输入的标题，而不是固定的 "重复事项"
            repeat_reminders.append({
                'title': title,  # 设置为用户输入的标题
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
        # 更新提醒事项表格
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.reminder_table.setRowCount(0)  # 清空现有内容

        # 按时间排序提醒事项
        self.reminders.sort(key=lambda r: r['remind_time'])

        # 显示提醒事项
        for reminder in self.reminders:
            if reminder['remind_time'].startswith(selected_date):
                remind_hour = int(reminder['remind_time'].split()[1].split(":")[0])
                remind_time = reminder['remind_time'].split()[1][:-3]

                row_position = self.reminder_table.rowCount()
                self.reminder_table.insertRow(row_position)

                # 更新表格内容
                self.reminder_table.setItem(row_position, 0, QTableWidgetItem(reminder['title']))
                self.reminder_table.setItem(row_position, 1, QTableWidgetItem(remind_time))

                # 设置居中对齐
                self.reminder_table.item(row_position, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.reminder_table.item(row_position, 1).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # 添加删除按钮
                delete_button = QPushButton("删除", self)
                delete_button.clicked.connect(lambda _, row=row_position: self.confirm_delete_reminder(row))
                self.reminder_table.setCellWidget(row_position, 2, delete_button)

    def confirm_delete_reminder(self, row):
        # 弹出二次确认窗口
        confirmation_dialog = QDialog(self)
        confirmation_dialog.setWindowTitle("确认删除")
        confirmation_layout = QVBoxLayout()

        confirmation_layout.addWidget(QLabel("您确定要删除该提醒事项吗？"))

        # 创建确认按钮和取消按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No)
        confirmation_layout.addWidget(button_box)

        confirmation_dialog.setLayout(confirmation_layout)

        button_box.button(QDialogButtonBox.StandardButton.Yes).clicked.connect(
            lambda: self.delete_reminder(row, confirmation_dialog))
        button_box.button(QDialogButtonBox.StandardButton.No).clicked.connect(confirmation_dialog.reject)

        confirmation_dialog.exec()

    def delete_reminder(self, row, confirmation_dialog):
        # 删除当前行的提醒事项
        reminder = self.reminders[row]

        if reminder['repeat']:
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    reminder_app = ReminderApp()
    reminder_app.show()
    sys.exit(app.exec())
