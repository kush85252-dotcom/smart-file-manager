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
"""