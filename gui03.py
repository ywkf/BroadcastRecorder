import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QLabel, QFrame, QSpacerItem, QSizePolicy, QScrollArea,
                             QListWidget, QListWidgetItem, QStackedWidget, QPushButton)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MaaDxxw - 0.1.0")

        # 整个界面背景为白色
        self.setStyleSheet("background:white;")

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建左侧导航栏
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        # 创建右侧内容区(使用QStackedWidget来切换页面)
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

        # 中部主导航菜单(使用QListWidget)
        nav_list = QListWidget()
        # 给导航菜单的item选中态和hover态加上圆角和适当的间距，以实现圆角选中效果
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

        # 默认选中第一个菜单项
        nav_list.setCurrentRow(0)

        nav_list.itemClicked.connect(self.on_nav_item_clicked)

        # 将主导航加入布局并使用滚动区域容纳
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background:white; border:none;")
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)
        nav_layout.addWidget(nav_list)
        nav_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # 底部菜单项
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
        # 首页页面按照提供的图片布局
        page_home = self.create_home_page()
        self.stack.addWidget(page_home)

        # 其余页面保持原有的demo样式不变
        page_device = self.create_demo_page("设备页面", Qt.GlobalColor.yellow)
        self.stack.addWidget(page_device)

        page_task = self.create_demo_page("任务页面", Qt.GlobalColor.green)
        self.stack.addWidget(page_task)

        page_task_set = self.create_demo_page("任务集页面", Qt.GlobalColor.cyan)
        self.stack.addWidget(page_task_set)

        page_log = self.create_demo_page("日志页面", Qt.GlobalColor.magenta)
        self.stack.addWidget(page_log)

    def create_home_page(self):
        # 按照图片布局创建首页页面
        home_widget = QWidget()
        home_widget.setStyleSheet("background:white;")
        main_layout = QHBoxLayout(home_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 左侧：今日待办事项 (圆角边框)
        todo_frame = QFrame()
        todo_frame.setFrameShape(QFrame.Shape.NoFrame)
        todo_layout = QVBoxLayout(todo_frame)
        todo_layout.setContentsMargins(20, 20, 20, 20)

        # 使用样式表为todo_frame设置圆角和边框
        todo_frame.setStyleSheet("""
            QFrame {
                background:white; 
                border:1px solid #ccc; 
                border-radius:10px;
            }
        """)

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
            # 设置列表字体大小
            item_font = QFont("Microsoft Yahei", 12)
            item.setFont(item_font)
            todo_list.addItem(item)

        todo_layout.addWidget(title_label)
        todo_layout.addWidget(todo_list)

        # 右侧：3个音频波形区域
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
            # 将波形框也设置为圆角边框
            waveform_frame.setStyleSheet("""
                background:white; 
                border:1px solid #ccc; 
                border-radius:10px;
            """)

            single_audio_layout.addWidget(audio_label)
            single_audio_layout.addWidget(waveform_frame)
            audio_layout.addWidget(single_audio_frame)

        # 加入主布局
        main_layout.addWidget(todo_frame)
        main_layout.addWidget(audio_frame)

        # 设置比例为9:11使待办事项稍窄于之前2:3，但比1:2更宽些，从而更加协调
        main_layout.setStretch(0, 9)
        main_layout.setStretch(1, 11)

        return home_widget

    def create_demo_page(self, text, color):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        color_q = QColor(color)
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Microsoft Yahei", 12, QFont.Weight.Bold))
        label.setStyleSheet(f"background:{color_q.name()}; border-radius:5px;")
        layout.addWidget(label, 1, Qt.AlignmentFlag.AlignCenter)

        button = QPushButton("这是一个按钮")
        layout.addWidget(button, 0, Qt.AlignmentFlag.AlignCenter)

        widget.setStyleSheet("background:white;")
        return widget

    def on_nav_item_clicked(self, item):
        # 根据点击的菜单项决定切换到哪个页面
        text = item.text()
        mapping = {
            "首页": 0,
            "设备": 1,
            "任务": 2,
            "任务集": 3,
            "日志": 4
        }
        if text in mapping:
            index = mapping[text]
            self.stack.setCurrentIndex(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
