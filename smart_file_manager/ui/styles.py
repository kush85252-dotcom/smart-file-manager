"""Application stylesheet."""

STYLESHEET = """
    QWidget {
        background: #111318;
        color: #e8e8e8;
        font-family: Segoe UI;
        font-size: 14px;
    }

    #sidebar {
        background: #181b21;
        border-right: 1px solid #292d35;
    }

    #appTitle {
        font-size: 28px;
        font-weight: bold;
        color: white;
    }

    #version {
        color: #858b98;
        font-size: 12px;
    }

    #sidebarInfo {
        color: #707784;
        padding: 10px;
    }

    QPushButton {
        background: #20242c;
        border: 1px solid #303541;
        border-radius: 8px;
        padding: 9px 14px;
    }

    QPushButton:hover {
        background: #292e38;
    }

    QPushButton:pressed {
        background: #323844;
    }

    #sidebarButton {
        text-align: left;
        padding: 13px;
        border: none;
        border-radius: 8px;
        color: #b8bec9;
    }

    #sidebarButton:hover {
        background: #242932;
        color: white;
    }

    QLineEdit {
        background: #191c22;
        border: 1px solid #303541;
        border-radius: 8px;
        padding: 9px;
        color: white;
    }

    QLineEdit:focus {
        border: 1px solid #5d6574;
    }

    #heading {
        font-size: 30px;
        font-weight: bold;
        color: white;
    }

    #sectionTitle {
        font-size: 20px;
        font-weight: bold;
        margin-top: 10px;
    }

    #location {
        color: #8d94a1;
    }

    #description {
        color: #969daa;
    }

    #card {
        background: #191c22;
        border: 1px solid #292d35;
        border-radius: 12px;
        padding: 10px;
    }

    #cardTitle {
        color: #9299a6;
        font-size: 13px;
    }

    #cardValue {
        color: white;
        font-size: 28px;
        font-weight: bold;
    }

    #categoryInfo {
        background: #191c22;
        border: 1px solid #292d35;
        border-radius: 10px;
        padding: 15px;
        color: #c4c9d2;
    }

    #preview {
        background: #191c22;
        border: 1px solid #292d35;
        border-radius: 10px;
        padding: 15px;
        color: #c4c9d2;
    }

    QTableWidget {
        background: #15181d;
        alternate-background-color: #191c22;
        border: 1px solid #292d35;
        border-radius: 8px;
        gridline-color: #252932;
        selection-background-color: #303641;
        selection-color: white;
    }

    QHeaderView::section {
        background: #1c2027;
        color: #aeb5c1;
        border: none;
        padding: 9px;
        font-weight: bold;
    }

    QProgressBar {
        background: #191c22;
        border: 1px solid #303541;
        border-radius: 7px;
        text-align: center;
        height: 18px;
    }

    QProgressBar::chunk {
        background: #555e6e;
        border-radius: 6px;
    }

    QMenu {
        background: #1b1e24;
        border: 1px solid #303541;
        padding: 5px;
    }

    QMenu::item {
        padding: 8px 30px 8px 10px;
        border-radius: 5px;
    }

    QMenu::item:selected {
        background: #2b3039;
    }

    #status {
        color: #777f8c;
        padding: 4px;
    }

    #settingsCard {
        background: #191c22;
        border: 1px solid #292d35;
        border-radius: 12px;
    }

    QCheckBox {
        spacing: 8px;
        color: #e8e8e8;
        background: transparent;
    }

    QComboBox {
        background: #191c22;
        border: 1px solid #303541;
        border-radius: 8px;
        padding: 8px;
        min-width: 180px;
    }

    QScrollArea {
        background: transparent;
    }

    QLabel {
        background: transparent;
    }

    #sidebarButton[current="true"] {
        background: #2a303b;
        color: white;
        font-weight: bold;
    }

    QPushButton:disabled {
        background: #181b21;
        border-color: #252932;
        color: #5f6672;
    }

    QListWidget {
        background: #15181d;
        alternate-background-color: #191c22;
        border: 1px solid #292d35;
        border-radius: 8px;
        padding: 4px;
    }

    QListWidget::item {
        padding: 8px;
        border-radius: 5px;
    }

    QListWidget::item:selected {
        background: #303641;
        color: white;
    }

    QCheckBox::indicator {
        width: 15px;
        height: 15px;
        border: 1px solid #4a5160;
        border-radius: 4px;
        background: #191c22;
    }

    QCheckBox::indicator:hover {
        border-color: #7b8599;
    }

    QCheckBox::indicator:checked {
        background: #5b8def;
        border-color: #5b8def;
    }

    QCheckBox::indicator:disabled {
        background: #181b21;
        border-color: #2c313b;
    }

    QLabel#statusDot {
        font-size: 16px;
        color: #777f8c;
    }

    QLabel#statusDot[state="running"] {
        color: #4cc38a;
    }

    QLabel#statusDot[state="error"] {
        color: #e5645f;
    }
"""


LIGHT_STYLESHEET = """
    QWidget {
        background: #f5f6f8;
        color: #20242c;
        font-family: Segoe UI;
        font-size: 14px;
    }
    #sidebar {
        background: #e9ebef;
        border-right: 1px solid #d5d9e0;
    }
    #appTitle { color: #171a20; font-size: 28px; font-weight: bold; }
    #heading { color: #171a20; font-size: 30px; font-weight: bold; }
    #sectionTitle { font-size: 20px; font-weight: bold; margin-top: 10px; }
    #cardValue { font-size: 28px; font-weight: bold; }
    #version, #sidebarInfo { font-size: 12px; }
    #version, #sidebarInfo, #description, #location, #status { color: #68707d; }
    QPushButton {
        background: #ffffff;
        border: 1px solid #cfd4dd;
        border-radius: 8px;
        padding: 9px 14px;
        color: #20242c;
    }
    QPushButton:hover { background: #eef1f5; }
    #sidebarButton { border: none; color: #4b5360; text-align: left; padding: 13px; }
    #sidebarButton:hover { background: #dce1e8; color: #171a20; }
    QLineEdit, QComboBox {
        background: #ffffff;
        border: 1px solid #cfd4dd;
        border-radius: 8px;
        padding: 9px;
        color: #20242c;
    }
    #card, #categoryInfo, #preview, #settingsCard {
        background: #ffffff;
        border: 1px solid #d5d9e0;
        border-radius: 12px;
    }
    #cardTitle { color: #68707d; }
    #cardValue { color: #171a20; }
    QTableWidget {
        background: #ffffff;
        alternate-background-color: #f4f5f7;
        border: 1px solid #d5d9e0;
        gridline-color: #e1e4e9;
        selection-background-color: #dbe7f7;
        selection-color: #171a20;
    }
    QHeaderView::section {
        background: #e9ebef;
        color: #4b5360;
        border: none;
        padding: 9px;
        font-weight: bold;
    }
    QProgressBar { background: #ffffff; border: 1px solid #cfd4dd; }
    QProgressBar::chunk { background: #6b7788; }
    QCheckBox { color: #20242c; background: transparent; }
    QScrollArea { background: transparent; }
    QLabel { background: transparent; }
    #sidebarButton[current="true"] { background: #d3d9e2; color: #171a20; font-weight: bold; }
    QPushButton:disabled { background: #eef0f3; border-color: #dde1e7; color: #9aa1ad; }
    QListWidget {
        background: #ffffff;
        alternate-background-color: #f4f5f7;
        border: 1px solid #d5d9e0;
        border-radius: 8px;
        padding: 4px;
    }
    QListWidget::item { padding: 8px; border-radius: 5px; }
    QListWidget::item:selected { background: #dbe7f7; color: #171a20; }
    QCheckBox::indicator {
        width: 15px;
        height: 15px;
        border: 1px solid #9aa3b2;
        border-radius: 4px;
        background: #ffffff;
    }
    QCheckBox::indicator:hover { border-color: #5b8def; }
    QCheckBox::indicator:checked { background: #3d78e0; border-color: #3d78e0; }
    QCheckBox::indicator:disabled { background: #eef0f3; border-color: #dde1e7; }
    QLabel#statusDot { font-size: 16px; color: #8b93a1; }
    QLabel#statusDot[state="running"] { color: #1f9d63; }
    QLabel#statusDot[state="error"] { color: #d23f3a; }
"""