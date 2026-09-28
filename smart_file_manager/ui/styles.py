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
    #appTitle, #heading { color: #171a20; }
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
    QCheckBox { color: #20242c; }
    QScrollArea { background: transparent; }
"""