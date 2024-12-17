import sys
import requests
from datetime import datetime
from PyQt6.QtCore import Qt, QUrl, QDateTime, QDate, QPoint, QTimer
from PyQt6.QtGui import QFont, QMouseEvent
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QLabel, QFrame, QSpacerItem, QSizePolicy, QScrollArea,
                             QListWidget, QListWidgetItem, QStackedWidget, QPushButton,
                             QLineEdit, QTableWidget, QTableWidgetItem, QComboBox,
                             QDialog, QMenu, QTextEdit, QSlider, QCalendarWidget)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

API_BASE = "http://127.0.0.1:8000"  # 根据实际地址修改

class CustomCalendarWidget(QCalendarWidget):
    # 自定义日历组件, 支持双击事件
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QCalendarWidget.SelectionMode.SingleSelection)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        super().mouseDoubleClickEvent(event)
        # 双击调用父组件函数更新日期
        self.parent().on_calendar_double_clicked()


class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20,20,20,20)
        main_layout.setSpacing(20)

        self.todo_frame = QFrame()
        self.todo_frame.setStyleSheet("""
            QFrame {
                background:white;
                border:1px solid #ccc;
                border-radius:10px;
            }
        """)
        self.todo_layout = QVBoxLayout(self.todo_frame)
        self.todo_layout.setContentsMargins(20,20,20,20)

        self.title_label = QLabel("今日待办事项:")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        self.title_label.setFont(title_font)

        self.todo_list = QListWidget()
        self.todo_list.setStyleSheet("background:white; border:none;")

        self.todo_layout.addWidget(self.title_label)
        self.todo_layout.addWidget(self.todo_list)

        audio_frame = QWidget()
        audio_layout = QVBoxLayout(audio_frame)
        audio_layout.setSpacing(20)
        audio_layout.setContentsMargins(20,20,20,20)
        audio_frame.setStyleSheet("background:white;")

        for i in range(1,4):
            single_audio_frame = QFrame()
            single_audio_layout = QVBoxLayout(single_audio_frame)
            single_audio_layout.setSpacing(5)
            single_audio_frame.setStyleSheet("background:white;")

            audio_label = QLabel(f"音频 {i}")
            audio_label.setFont(QFont("Microsoft Yahei", 10, QFont.Weight.Bold))

            waveform_frame = QFrame()
            waveform_frame.setFrameShape(QFrame.Shape.Panel)
            waveform_frame.setFrameShadow(QFrame.Shadow.Raised)
            waveform_frame.setMinimumSize(200,80)
            waveform_frame.setStyleSheet("""
                background:white;
                border:1px solid #ccc;
                border-radius:10px;
            """)

            single_audio_layout.addWidget(audio_label)
            single_audio_layout.addWidget(waveform_frame)
            audio_layout.addWidget(single_audio_frame)

        main_layout.addWidget(self.todo_frame)
        main_layout.addWidget(audio_frame)
        main_layout.setStretch(0,9)
        main_layout.setStretch(1,11)

        self.update_today_reminders()

    def update_today_reminders(self):
        try:
            response = requests.get(f"{API_BASE}/api/reminders/today")
            if response.status_code == 200:
                today_reminders = response.json()
                self.update_todo_list(today_reminders)
            else:
                print("Failed to fetch today's reminders:", response.status_code, response.text)
        except Exception as e:
            print("Error fetching today's reminders:", e)

    def update_todo_list(self, reminders):
        self.todo_list.clear()
        reminders.sort(key=lambda r: r['remind_at'])
        for r in reminders:
            time_part = r['remind_at'].split("T")[1][:-3]
            item = QListWidgetItem(f"{time_part}    {r['title']}")
            item_font = QFont("Microsoft Yahei", 12)
            item.setFont(item_font)
            self.todo_list.addItem(item)


class TaskPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.end_date = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20,20,20,20)
        main_layout.setSpacing(20)

        # 自定义日历风格，使其更统一
        self.calendar = CustomCalendarWidget(self)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background:white;
                border:1px solid #ccc;
                border-radius:10px;
            }
            /* 改进日历箭头按钮样式，以符合整体风格 */
            QCalendarWidget QToolButton {
                background:#cce0ff;
                border:none;
                border-radius:5px;
                padding:2px 5px;
                margin:2px;
            }
            QCalendarWidget QToolButton:hover {
                background:#b3d1ff;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background:white;
                selection-background-color:#cce0ff;
                selection-color:black;
                border-radius:5px;
            }
        """)
        self.calendar.selectionChanged.connect(self.update_reminders)
        self.calendar.setSelectedDate(QDate.currentDate()) # 默认选中今天

        main_layout.addWidget(self.calendar)

        # 事项列表区域(圆角边框)
        reminder_frame = QFrame()
        reminder_frame.setStyleSheet("background:white; border:1px solid #ccc; border-radius:10px;")
        reminder_layout = QVBoxLayout(reminder_frame)
        reminder_layout.setContentsMargins(10,10,10,10)
        reminder_layout.setSpacing(10)

        top_line_layout = QHBoxLayout()
        title_label = QLabel("事项列表")
        title_label.setStyleSheet("QLabel {border:none; font-weight:bold; font-size:14px;}")
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background:#cce0ff; border:none; border-radius:5px; padding:5px;
            }
            QPushButton:hover { background:#b3d1ff; }
        """)
        self.refresh_button.clicked.connect(self.update_reminders)
        top_line_layout.addWidget(title_label)
        top_line_layout.addStretch()
        top_line_layout.addWidget(self.refresh_button)
        reminder_layout.addLayout(top_line_layout)

        self.reminder_table = QTableWidget(self)
        self.reminder_table.setRowCount(0)
        self.reminder_table.setColumnCount(2)
        self.reminder_table.setHorizontalHeaderLabels(["时间","标题"])
        self.reminder_table.setColumnWidth(0,100)
        self.reminder_table.setColumnWidth(1,300)
        self.reminder_table.setStyleSheet("""
            QTableWidget {
                background:white;
                border:none;
                gridline-color:#ddd;
            }
            QHeaderView::section {
                background:white;
                border:none;
                font-weight:bold;
            }
        """)
        self.reminder_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.reminder_table.customContextMenuRequested.connect(self.show_context_menu)
        reminder_layout.addWidget(self.reminder_table)
        main_layout.addWidget(reminder_frame)

        add_reminder_layout = QVBoxLayout()
        add_reminder_layout.setSpacing(10)

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

        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("请输入标题")
        self.title_input.setStyleSheet("QLineEdit { background:white; border:none; border-radius:5px; padding:5px;}")

        today = QDate.currentDate()

        # 年、月、日、时、分、重复、结束日期同一行
        line1_layout = QHBoxLayout()
        line1_layout.setSpacing(10)
        self.year_label = QLabel("年:")
        self.year_label.setStyleSheet("QLabel { border:none; }")
        self.year_input = create_combo_box(range(1900,2101), today.year())

        self.month_label = QLabel("月:")
        self.month_label.setStyleSheet("QLabel { border:none; }")
        self.month_input = create_combo_box(range(1,13), today.month())

        self.day_label = QLabel("日:")
        self.day_label.setStyleSheet("QLabel { border:none; }")
        self.day_input = create_combo_box(range(1,32), today.day())

        self.hour_label = QLabel("时:")
        self.hour_label.setStyleSheet("QLabel { border:none; }")
        self.hour_input = create_combo_box(range(0,24),12)

        self.minute_label = QLabel("分:")
        self.minute_label.setStyleSheet("QLabel { border:none; }")
        self.minute_input = create_combo_box(range(0,60),30)

        self.repeat_label = QLabel("重复:")
        self.repeat_label.setStyleSheet("QLabel { border:none; }")
        self.repeat_checkbox = create_combo_box(["不重复","每天","每周","每月","每年"],"不重复")
        self.repeat_checkbox.currentIndexChanged.connect(self.toggle_end_date_visibility)

        self.end_date_button = QPushButton("选择结束日期",self)
        self.end_date_button.setVisible(False)
        self.end_date_button.setStyleSheet("""
            QPushButton {
                background:white; 
                border:none; 
                border-radius:5px;
                padding:5px;
            }
            QPushButton:hover { background:#e7f1ff; }
        """)
        self.end_date_button.clicked.connect(self.open_end_date_calendar)

        for w in [self.year_label,self.year_input,self.month_label,self.month_input,self.day_label,self.day_input,
                  self.hour_label,self.hour_input,self.minute_label,self.minute_input,
                  self.repeat_label,self.repeat_checkbox,self.end_date_button]:
            line1_layout.addWidget(w)

        # 标题输入与添加提醒同一行
        line2_layout = QHBoxLayout()
        line2_layout.setSpacing(10)
        line2_layout.addWidget(self.title_input)
        self.add_button = QPushButton("添加提醒",self)
        self.add_button.setStyleSheet("""
            QPushButton {
                background:#cce0ff; 
                border:none; 
                border-radius:5px; 
                padding:5px;
            }
            QPushButton:hover { background:#b3d1ff; }
        """)
        self.add_button.clicked.connect(self.add_reminder)
        line2_layout.addWidget(self.add_button)
        line2_layout.addStretch()

        add_reminder_layout.addLayout(line1_layout)
        add_reminder_layout.addLayout(line2_layout)

        main_layout.addLayout(add_reminder_layout)
        self.setLayout(main_layout)

        self.update_reminders()

    def on_calendar_double_clicked(self):
        # 双击日历后更新日期选择
        selected_date = self.calendar.selectedDate()
        self.year_input.setCurrentText(str(selected_date.year()))
        self.month_input.setCurrentText(str(selected_date.month()))
        self.day_input.setCurrentText(str(selected_date.day()))

    def toggle_end_date_visibility(self):
        if self.repeat_checkbox.currentText() == "不重复":
            self.end_date_button.setVisible(False)
        else:
            self.end_date_button.setVisible(True)

    def open_end_date_calendar(self):
        calendar_dialog = QDialog(self)
        calendar_dialog.setWindowTitle("选择结束日期")
        calendar_layout = QVBoxLayout(calendar_dialog)

        calendar_widget = QCalendarWidget(self)
        calendar_widget.setSelectionMode(QCalendarWidget.SelectionMode.SingleSelection)
        # 同样的风格使日历统一
        calendar_widget.setStyleSheet("""
            QCalendarWidget {
                background:white; 
                border:1px solid #ccc;
                border-radius:10px;
            }
            QCalendarWidget QToolButton {
                background:#cce0ff;
                border:none;
                border-radius:5px;
                padding:2px 5px;
                margin:2px;
            }
            QCalendarWidget QToolButton:hover {
                background:#b3d1ff;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background:white;
                selection-background-color:#cce0ff;
                selection-color:black;
                border-radius:5px;
            }
        """)
        calendar_layout.addWidget(calendar_widget)

        never_button = QPushButton("永不", self)
        never_button.setStyleSheet("QPushButton {background:white; border:none; border-radius:5px; padding:5px;} QPushButton:hover{background:#e7f1ff;}")
        never_button.clicked.connect(lambda: self.set_end_date(None, calendar_dialog))

        select_button = QPushButton("选择", self)
        select_button.setStyleSheet("QPushButton {background:#cce0ff; border:none; border-radius:5px; padding:5px;} QPushButton:hover{background:#b3d1ff;}")
        select_button.clicked.connect(lambda: self.set_end_date(calendar_widget.selectedDate(), calendar_dialog))
        calendar_layout.addWidget(never_button)
        calendar_layout.addWidget(select_button)

        calendar_dialog.exec()

    def set_end_date(self, selected_date, dialog):
        if selected_date is None:
            self.end_date = None
        else:
            self.end_date = selected_date.toString("yyyy-MM-dd")
        self.end_date_button.setText(f"结束日期: {self.end_date if self.end_date else '无'}")
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
            # 若重复选择不是不重复,但没有结束日期,默认只重复一次(与不重复相同)
            # 这里直接POST一次即可
            data = {
                "title": title,
                "description": "",
                "remind_at": remind_datetime
            }
            try:
                r = requests.post(f"{API_BASE}/api/reminders", json=data)
                if r.status_code == 200:
                    self.update_reminders()
                else:
                    print("添加提醒失败:", r.status_code, r.text)
            except Exception as e:
                print("添加提醒请求失败:", e)
            self.title_input.clear()
        else:
            self.show_error_dialog("提醒事项标题不能为空")

    def update_reminders(self):
        selected_date_str = self.calendar.selectedDate().toString("yyyy-MM-dd")
        try:
            r = requests.get(f"{API_BASE}/api/reminders")
            if r.status_code == 200:
                all_reminders = r.json()
                day_reminders = [rem for rem in all_reminders if rem['remind_at'].startswith(selected_date_str)]
                self.reminder_table.setRowCount(0)
                day_reminders.sort(key=lambda x: x['remind_at'])
                for rem in day_reminders:
                    row_position = self.reminder_table.rowCount()
                    self.reminder_table.insertRow(row_position)
                    time_part = rem['remind_at'].split("T")[1][:-3]
                    self.reminder_table.setItem(row_position,0,QTableWidgetItem(time_part))
                    self.reminder_table.setItem(row_position,1,QTableWidgetItem(rem['title']))
                    self.reminder_table.item(row_position,0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.reminder_table.item(row_position,1).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                print("获取事项失败:", r.status_code, r.text)
        except Exception as e:
            print("获取事项请求失败:", e)

    def show_context_menu(self, pos: QPoint):
        item = self.reminder_table.itemAt(pos)
        if item is not None:
            row = item.row()
            menu = QMenu(self)
            delete_action = menu.addAction("删除")
            delete_action.triggered.connect(lambda: self.delete_reminder_by_row(row))
            menu.exec(self.reminder_table.mapToGlobal(pos))

    def delete_reminder_by_row(self, row):
        selected_date_str = self.calendar.selectedDate().toString("yyyy-MM-dd")
        time_str = self.reminder_table.item(row,0).text()
        title = self.reminder_table.item(row,1).text()
        remind_datetime = f"{selected_date_str} {time_str}:00"
        try:
            r = requests.get(f"{API_BASE}/api/reminders")
            if r.status_code == 200:
                all_reminders = r.json()
                target = None
                for rem in all_reminders:
                    dt_str = rem['remind_at'].replace("T"," ")
                    if rem['title'] == title and dt_str.startswith(selected_date_str) and dt_str[11:16] == time_str:
                        target = rem
                        break
                if target:
                    del_r = requests.delete(f"{API_BASE}/api/reminders/{target['id']}")
                    if del_r.status_code == 200:
                        self.update_reminders()
                    else:
                        print("删除提醒失败:", del_r.status_code, del_r.text)
                else:
                    print("未找到要删除的提醒事项")
            else:
                print("获取事项列表失败:", r.status_code, r.text)
        except Exception as e:
            print("删除提醒请求失败:", e)

    def show_error_dialog(self, message):
        dialog = QDialog(self)
        dialog.setWindowTitle("错误")
        layout = QVBoxLayout()
        layout.addWidget(QLabel(message))
        dialog.setLayout(layout)
        dialog.exec()


class VolumePopup(QDialog):
    def __init__(self, parent=None, audio_output=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.audio_output = audio_output

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5,5,5,5)
        layout.setSpacing(5)

        # 垂直音量滑块
        self.volume_slider = QSlider(Qt.Orientation.Vertical)
        self.volume_slider.setRange(0,100)
        if self.audio_output:
            self.volume_slider.setValue(int(self.audio_output.volume()*100))
        else:
            self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.change_volume)

        layout.addWidget(self.volume_slider)

    def change_volume(self, value):
        if self.audio_output:
            self.audio_output.setVolume(value/100.0)


class AudioPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20,20,20,20)
        main_layout.setSpacing(20)

        file_frame = QFrame()
        file_frame.setStyleSheet("background:white; border:1px solid #ccc; border-radius:10px;")
        file_layout = QVBoxLayout(file_frame)
        file_layout.setContentsMargins(10,10,10,10)
        file_layout.setSpacing(10)

        top_line_layout = QHBoxLayout()
        title_label = QLabel("音频文件")
        title_label.setStyleSheet("QLabel {border:none; font-weight:bold; font-size:14px;}")
        refresh_btn = QPushButton("刷新")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background:#cce0ff; border:none; border-radius:5px; padding:5px;
            }
            QPushButton:hover {background:#b3d1ff;}
        """)
        refresh_btn.clicked.connect(self.load_audio_files)

        top_line_layout.addWidget(title_label)
        top_line_layout.addStretch()
        top_line_layout.addWidget(refresh_btn)

        file_layout.addLayout(top_line_layout)

        self.audio_list = QListWidget()
        self.audio_list.setStyleSheet("background:white; border:none;")
        self.audio_list.itemClicked.connect(self.on_audio_item_clicked)
        file_layout.addWidget(self.audio_list)

        main_layout.addWidget(file_frame)

        # 播放器区域紧凑
        player_frame = QFrame()
        player_frame.setStyleSheet("background:white; border:1px solid #ccc; border-radius:10px;")
        # 减少内边距和间距
        player_layout = QHBoxLayout(player_frame)
        player_layout.setContentsMargins(10,10,10,10)
        player_layout.setSpacing(5)

        left_player_layout = QVBoxLayout()
        left_player_layout.setSpacing(5)

        controls_layout = QHBoxLayout()
        circle_btn_style = """
            QPushButton {
                background:#cce0ff; 
                border:none; 
                border-radius:20px;
                width:40px; height:40px;
            }
            QPushButton:hover { background:#b3d1ff; }
        """

        self.prev_button = QPushButton("上一首")
        self.prev_button.setStyleSheet(circle_btn_style)
        self.prev_button.clicked.connect(self.prev_track)

        self.play_button = QPushButton("播放/暂停")
        self.play_button.setStyleSheet(circle_btn_style)
        self.play_button.clicked.connect(self.toggle_play)

        self.next_button = QPushButton("下一首")
        self.next_button.setStyleSheet(circle_btn_style)
        self.next_button.clicked.connect(self.next_track)

        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.next_button)

        left_player_layout.addLayout(controls_layout)

        progress_layout = QHBoxLayout()
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0,1000)
        self.progress_slider.sliderMoved.connect(self.seek_position)
        self.progress_slider.setFixedWidth(200)
        progress_layout.addWidget(self.progress_slider)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("QLabel{border:none;}")
        progress_layout.addWidget(self.time_label)

        left_player_layout.addLayout(progress_layout)
        player_layout.addLayout(left_player_layout)

        # 喇叭按钮，点击弹出音量调节
        self.volume_button = QPushButton("🔊")
        self.volume_button.setStyleSheet("""
            QPushButton {
                background:#cce0ff; border:none; border-radius:20px; width:40px; height:40px;
            }
            QPushButton:hover {background:#b3d1ff;}
        """)
        self.volume_button.clicked.connect(self.toggle_volume_popup)
        player_layout.addWidget(self.volume_button, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.volume_popup = None

        main_layout.addWidget(player_frame)
        self.setLayout(main_layout)

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_slider)
        self.timer.start(500)

        self.current_track_index = -1
        self.load_audio_files()
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)

    def toggle_volume_popup(self):
        if self.volume_popup and self.volume_popup.isVisible():
            self.volume_popup.close()
            self.volume_popup = None
        else:
            self.volume_popup = VolumePopup(audio_output=self.audio_output, parent=self)
            # 在音量按钮右侧或下方显示
            pos = self.volume_button.mapToGlobal(self.volume_button.rect().bottomRight())
            self.volume_popup.move(pos)
            self.volume_popup.show()

    def load_audio_files(self):
        try:
            r = requests.get(f"{API_BASE}/recordings")
            if r.status_code == 200:
                files = r.json()
                self.audio_list.clear()
                for f in files:
                    filename = f['filename']
                    item = QListWidgetItem(filename)
                    item.setData(Qt.ItemDataRole.UserRole, filename)
                    self.audio_list.addItem(item)
            else:
                print("获取音频列表失败:", r.status_code, r.text)
        except Exception as e:
            print("获取音频列表请求失败:", e)

    def on_audio_item_clicked(self, item):
        filename = item.data(Qt.ItemDataRole.UserRole)
        audio_url = f"{API_BASE}/recordings/{filename}"
        self.player.setSource(QUrl(audio_url))
        self.player.stop()
        self.play_button.setText("播放/暂停")
        self.current_track_index = self.audio_list.indexFromItem(item).row()

    def toggle_play(self):
        if self.player.source().isEmpty():
            return
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def prev_track(self):
        if self.audio_list.count() == 0:
            return
        if self.current_track_index > 0:
            self.current_track_index -= 1
            item = self.audio_list.item(self.current_track_index)
            self.on_audio_item_clicked(item)
            self.player.play()

    def next_track(self):
        if self.audio_list.count() == 0:
            return
        if self.current_track_index < self.audio_list.count()-1:
            self.current_track_index += 1
            item = self.audio_list.item(self.current_track_index)
            self.on_audio_item_clicked(item)
            self.player.play()

    def update_slider(self):
        if self.player.duration() > 0:
            pos = self.player.position()
            dur = self.player.duration()
            value = int((pos/dur)*1000)
            self.progress_slider.blockSignals(True)
            self.progress_slider.setValue(value)
            self.progress_slider.blockSignals(False)

            current_sec = pos//1000
            total_sec = dur//1000
            current_min = current_sec//60
            current_sec = current_sec%60
            total_min = total_sec//60
            total_sec = total_sec%60
            self.time_label.setText(f"{current_min:02d}:{current_sec:02d} / {total_min:02d}:{total_sec:02d}")
        else:
            self.time_label.setText("00:00 / 00:00")

    def seek_position(self, value):
        if self.player.duration() > 0:
            dur = self.player.duration()
            pos = int((value/1000)*dur)
            self.player.setPosition(pos)

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.next_track()


class VolumePopup(QDialog):
    def __init__(self, parent=None, audio_output=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.audio_output = audio_output

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5,5,5,5)
        layout.setSpacing(5)

        self.volume_slider = QSlider(Qt.Orientation.Vertical)
        self.volume_slider.setRange(0,100)
        if self.audio_output:
            self.volume_slider.setValue(int(self.audio_output.volume()*100))
        else:
            self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.change_volume)

        layout.addWidget(self.volume_slider)

    def change_volume(self, value):
        if self.audio_output:
            self.audio_output.setVolume(value/100.0)


class TextPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20,20,20,20)
        main_layout.setSpacing(20)

        file_frame = QFrame()
        file_frame.setStyleSheet("background:white; border:1px solid #ccc; border-radius:10px;")
        file_layout = QVBoxLayout(file_frame)
        file_layout.setContentsMargins(10,10,10,10)
        file_layout.setSpacing(10)

        top_line_layout = QHBoxLayout()
        title_label = QLabel("文本文件")
        title_label.setStyleSheet("QLabel {border:none; font-weight:bold; font-size:14px;}")
        refresh_btn = QPushButton("刷新")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background:#cce0ff; border:none; border-radius:5px; padding:5px;
            }
            QPushButton:hover {background:#b3d1ff;}
        """)
        refresh_btn.clicked.connect(self.load_text_files)

        top_line_layout.addWidget(title_label)
        top_line_layout.addStretch()
        top_line_layout.addWidget(refresh_btn)
        file_layout.addLayout(top_line_layout)

        self.text_list = QListWidget()
        self.text_list.setStyleSheet("background:white; border:none;")
        self.text_list.itemClicked.connect(self.on_text_item_clicked)
        file_layout.addWidget(self.text_list)

        main_layout.addWidget(file_frame)

        self.text_view = QTextEdit()
        self.text_view.setStyleSheet("""
            QTextEdit {
                background:white;
                border:1px solid #ccc;
                border-radius:10px;
                font-size:16px;
            }
        """)
        self.text_view.setReadOnly(True)

        main_layout.addWidget(self.text_view)
        main_layout.setStretch(0,1)
        main_layout.setStretch(1,3)

        self.setLayout(main_layout)
        self.load_text_files()

    def load_text_files(self):
        try:
            r = requests.get(f"{API_BASE}/transcriptions")
            if r.status_code == 200:
                files = r.json()
                self.text_list.clear()
                for f in files:
                    filename = f['filename']
                    item = QListWidgetItem(filename)
                    item.setData(Qt.ItemDataRole.UserRole, filename)
                    self.text_list.addItem(item)
            else:
                print("获取文本文件列表失败:", r.status_code, r.text)
        except Exception as e:
            print("获取文本文件列表请求失败:", e)

    def on_text_item_clicked(self, item):
        filename = item.data(Qt.ItemDataRole.UserRole)
        try:
            r = requests.get(f"{API_BASE}/transcriptions/{filename}")
            if r.status_code == 200:
                data = r.json()
                self.text_view.setPlainText(data['content'])
            else:
                print("获取文本内容失败:", r.status_code, r.text)
        except Exception as e:
            print("获取文本内容请求失败:", e)


class LogPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.log_view = QTextEdit()
        self.log_view.setStyleSheet("""
            QTextEdit {
                background:white;
                border:1px solid #ccc;
                border-radius:10px;
                font-size:14px;
            }
        """)
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)
        self.setLayout(layout)
        self.load_logs()

    def load_logs(self):
        try:
            r = requests.get(f"{API_BASE}/api/logs")
            if r.status_code == 200:
                data = r.json()
                self.log_view.setPlainText(data['content'])
            else:
                print("获取日志失败:", r.status_code, r.text)
        except Exception as e:
            print("获取日志请求失败:", e)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MaaDxxw - 0.1.0")
        self.resize(1200,700)

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)

        self.create_pages()

        self.setCentralWidget(main_widget)

    def create_sidebar(self):
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0,0,0,0)
        sidebar_layout.setSpacing(0)

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

        main_menu = ["首页","任务","音频","文本","日志"]
        for item_text in main_menu:
            nav_list.addItem(QListWidgetItem(item_text))

        nav_list.setCurrentRow(0)
        nav_list.itemClicked.connect(self.on_nav_item_clicked)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background:white; border:none;")
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0,0,0,0)
        nav_layout.setSpacing(0)
        nav_layout.addWidget(nav_list)
        nav_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        footer_menu = ["停止","检查资源包","检查更新","设置","关于"]
        for i,item_text in enumerate(footer_menu):
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
        self.page_home = HomePage()
        self.stack.addWidget(self.page_home)

        self.page_task = TaskPage()
        self.stack.addWidget(self.page_task)

        self.page_audio = AudioPage()
        self.stack.addWidget(self.page_audio)

        self.page_text = TextPage()
        self.stack.addWidget(self.page_text)

        self.page_log = LogPage()
        self.stack.addWidget(self.page_log)

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
