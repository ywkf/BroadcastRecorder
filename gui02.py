import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPixmap
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QLabel, QFrame, QSpacerItem, QSizePolicy, QScrollArea,
                             QListWidget, QListWidgetItem, QStackedWidget, QPushButton)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MaaDxxw - 0.1.0")

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0,0,0,0)
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
        sidebar_layout.setContentsMargins(0,0,0,0)
        sidebar_layout.setSpacing(0)

        # 中部主导航菜单(使用QListWidget)
        nav_list = QListWidget()
        nav_list.setStyleSheet("QListWidget{border:none;} QListWidget::item {padding:10px; border-bottom:1px solid #ddd;} QListWidget::item:hover{background:#e7f1ff;} QListWidget::item:selected{background:#cce0ff;}")
        nav_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        main_menu = ["首页","任务","音频","文本","日志"]
        for item_text in main_menu:
            item = QListWidgetItem(item_text)
            nav_list.addItem(item)

        # 默认选中第一个菜单项
        nav_list.setCurrentRow(0)

        nav_list.itemClicked.connect(self.on_nav_item_clicked)

        # 将主导航加入布局并使用滚动区域容纳
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0,0,0,0)
        nav_layout.setSpacing(0)
        nav_layout.addWidget(nav_list)
        nav_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # 底部菜单项
        footer_menu = ["停止","检查资源包","检查更新","设置","关于"]
        for i, item_text in enumerate(footer_menu):
            footer_label = QLabel(item_text)
            footer_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            style = "padding:8px 12px; border-bottom:1px solid #ddd;"
            if i == 0:
                style = "padding:8px 12px; border-top:1px solid #ddd; border-bottom:1px solid #ddd;"
            footer_label.setStyleSheet(style)
            nav_layout.addWidget(footer_label)

        scroll_area.setWidget(nav_container)
        sidebar_layout.addWidget(scroll_area)

        sidebar_widget.setFixedWidth(200)
        return sidebar_widget

    def create_pages(self):
        # 为stackedwidget创建5个示例页面
        # 在实际应用中，可在这里加载真实的UI组件。

        # 首页页面
        page_home = self.create_demo_page("首页页面", Qt.GlobalColor.lightGray)
        self.stack.addWidget(page_home)

        # 设备页面
        page_device = self.create_demo_page("设备页面", Qt.GlobalColor.yellow)
        self.stack.addWidget(page_device)

        # 任务页面
        page_task = self.create_demo_page("任务页面", Qt.GlobalColor.green)
        self.stack.addWidget(page_task)

        # 任务集页面
        page_task_set = self.create_demo_page("任务集页面", Qt.GlobalColor.cyan)
        self.stack.addWidget(page_task_set)

        # 日志页面
        page_log = self.create_demo_page("日志页面", Qt.GlobalColor.magenta)
        self.stack.addWidget(page_log)

    def create_demo_page(self, text, color):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 将全局色转换为QColor
        color_q = QColor(color)

        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Microsoft Yahei", 12, QFont.Weight.Bold))
        # 使用QColor的name()方法获取颜色的十六进制表示
        label.setStyleSheet(f"background:{color_q.name()}; border-radius:5px;")
        layout.addWidget(label, 1, Qt.AlignmentFlag.AlignCenter)

        # 示例增加一个按钮
        button = QPushButton("这是一个按钮")
        layout.addWidget(button, 0, Qt.AlignmentFlag.AlignCenter)

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
