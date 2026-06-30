import os
import sys
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QTableWidget, QTableWidgetItem, 
    QStackedWidget, QFrame, QHeaderView, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

# --- CONFIGURATION & STYLESHEET (Discord/Steam Cyberpunk Theme) ---
THEME_STYLE = """
    QMainWindow {
        background-color: #1E1E1E;
    }
    QWidget {
        color: #E0E0E0;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-size: 13px;
    }
    /* Sidebar styling */
    QFrame#Sidebar {
        background-color: #121212;
        border-right: 1px solid #2D2D2D;
    }
    QPushButton#SidebarBtn {
        background-color: transparent;
        color: #AAAAAA;
        border: none;
        border-radius: 6px;
        padding: 12px;
        text-align: left;
        font-weight: bold;
    }
    QPushButton#SidebarBtn:hover {
        background-color: #252525;
        color: #00E5FF; /* Electric Blue */
    }
    QPushButton#SidebarBtn:checked {
        background-color: #B026FF; /* Neon Purple */
        color: #FFFFFF;
    }
    /* Dashboard Cards */
    QFrame#Card {
        background-color: #252525;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 15px;
    }
    QLabel#CardTitle {
        font-size: 16px;
        font-weight: bold;
        color: #00E5FF;
    }
    QLabel#DashboardHeader {
        font-size: 24px;
        font-weight: bold;
        color: #FFFFFF;
        margin-bottom: 10px;
    }
    /* Action Buttons */
    QPushButton#PrimaryBtn {
        background-color: #B026FF;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: bold;
    }
    QPushButton#PrimaryBtn:hover {
        background-color: #C555FF;
    }
    QPushButton#SecondaryBtn {
        background-color: #252525;
        color: #00E5FF;
        border: 1px solid #00E5FF;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: bold;
    }
    QPushButton#SecondaryBtn:hover {
        background-color: rgba(0, 229, 255, 0.1);
    }
    /* Tables */
    QTableWidget {
        background-color: #151515;
        border: 1px solid #333333;
        gridline-color: #252525;
        border-radius: 6px;
    }
    QHeaderView::section {
        background-color: #121212;
        color: #AAAAAA;
        padding: 6px;
        border: none;
        border-bottom: 1px solid #333333;
        font-weight: bold;
    }
    QTableWidget::item {
        padding: 5px;
    }
"""

class SmartFileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SMART FILE MANAGER // AI EDITION")
        self.resize(1050, 650)
        self.setStyleSheet(THEME_STYLE)
        
        # State tracking vars
        self.selected_directory = ""
        self.scanned_files = []
        self.pending_moves = [] # Track changes for preview/confirmation
        self.history_log = []   # Command Pattern undo stack
        
        # Define Category Extension Mappings (AI rule base)
        self.extension_map = {
            'Pictures': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'],
            'Videos': ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'],
            'Music': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
            'Documents': ['.pdf', '.docx', '.doc', '.xlsx', '.pptx', '.txt', '.md'],
            'Software & Games': ['.exe', '.msi', '.apk', '.iso', '.dmg'],
            'Code Files': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.json', '.sh']
        }

        self.init_ui()

    def init_ui(self):
        # Main layout structure
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------------- SIDEBAR AREA ----------------
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 30, 15, 30)
        sidebar_layout.setSpacing(10)

        # Branding
        brand_label = QLabel("⚡ SMART FM")
        brand_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #B026FF; margin-bottom: 20px;")
        sidebar_layout.addWidget(brand_label)

        # Nav Buttons
        self.btn_home = QPushButton("  📊 Dashboard")
        self.btn_scan = QPushButton("  🔍 Scan & Organize")
        
        for btn in [self.btn_home, self.btn_scan]:
            btn.setObjectName("SidebarBtn")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            sidebar_layout.addWidget(btn)

        self.btn_home.setChecked(True)
        self.btn_home.clicked.connect(lambda: self.switch_page(0))
        self.btn_scan.clicked.connect(lambda: self.switch_page(1))

        sidebar_layout.addStretch()
        
        # Bottom system status label
        self.lbl_status = QLabel("System Status: Ready")
        self.lbl_status.setStyleSheet("color: #666666; font-size: 11px;")
        sidebar_layout.addWidget(self.lbl_status)
        
        main_layout.addWidget(sidebar)

        # ---------------- MAIN WINDOW VIEWS (ST_STACK) ----------------
        self.page_container = QStackedWidget()
        main_layout.addWidget(self.page_container)

        self.setup_dashboard_page()
        self.setup_workspace_page()

    # --- VIEW 1: DASHBOARD ---
    def setup_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header = QLabel("Welcome to the Future of File Management")
        header.setObjectName("DashboardHeader")
        layout.addWidget(header)

        # Cards Layout
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        # Card 1: Directory Info
        self.card_dir = QFrame()
        self.card_dir.setObjectName("Card")
        dir_layout = QVBoxLayout(self.card_dir)
        dir_title = QLabel("Target Zone")
        dir_title.setObjectName("CardTitle")
        self.lbl_current_dir_display = QLabel("No active directory loaded.")
        self.lbl_current_dir_display.setWordWrap(True)
        dir_layout.addWidget(dir_title)
        dir_layout.addWidget(self.lbl_current_dir_display)
        cards_layout.addWidget(self.card_dir)

        # Card 2: Quick Stats
        self.card_stats = QFrame()
        self.card_stats.setObjectName("Card")
        stats_layout = QVBoxLayout(self.card_stats)
        stats_title = QLabel("AI Statistics")
        stats_title.setObjectName("CardTitle")
        self.lbl_stat_counter = QLabel("Files Managed: 0\nLast Scan Result: N/A")
        stats_layout.addWidget(stats_title)
        stats_layout.addWidget(self.lbl_stat_counter)
        cards_layout.addWidget(self.card_stats)

        layout.addLayout(cards_layout)

        # Action Core
        action_box = QFrame()
        action_box.setObjectName("Card")
        action_layout = QHBoxLayout(action_box)
        
        ai_prompt_mock = QLabel("🤖 <b>AI Assistant:</b> \"Ready to scrub your dirty folders. Load a target zone to begin.\"")
        btn_quick_load = QPushButton("Select Target Folder")
        btn_quick_load.setObjectName("PrimaryBtn")
        btn_quick_load.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_quick_load.clicked.connect(self.select_directory)

        action_layout.addWidget(ai_prompt_mock)
        action_layout.addStretch()
        action_layout.addWidget(btn_quick_load)
        layout.addWidget(action_box)
        
        layout.addStretch()
        self.page_container.addWidget(page)

    # --- VIEW 2: WORKSPACE (SCANNER/ORGANIZER) ---
    def setup_workspace_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Action Toolbar
        toolbar = QHBoxLayout()
        self.btn_run_scan = QPushButton("⚡ Target Directory")
        self.btn_run_scan.setObjectName("SecondaryBtn")
        self.btn_run_scan.clicked.connect(self.select_directory)

        self.btn_ai_organize = QPushButton("✨ Run AI Sorcery")
        self.btn_ai_organize.setObjectName("PrimaryBtn")
        self.btn_ai_organize.setEnabled(False)
        self.btn_ai_organize.clicked.connect(self.generate_ai_organization_preview)

        self.btn_undo = QPushButton("↩️ Undo Last Action")
        self.btn_undo.setObjectName("SecondaryBtn")
        self.btn_undo.setEnabled(False)
        self.btn_undo.clicked.connect(self.undo_last_action)

        toolbar.addWidget(self.btn_run_scan)
        toolbar.addWidget(self.btn_ai_organize)
        toolbar.addWidget(self.btn_undo)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Workspace Tables Split View
        self.table_files = QTableWidget(0, 4)
        self.table_files.setHorizontalHeaderLabels(["File Name", "Size (KB)", "Type Extension", "AI Recommendation Plan"])
        self.table_files.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_files.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_files.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table_files)

        self.page_container.addWidget(page)

    # --- APPLICATION LOGIC ---
    def switch_page(self, index):
        self.btn_home.setChecked(index == 0)
        self.btn_scan.setChecked(index == 1)
        self.page_container.setCurrentIndex(index)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Open Dirty Workspace Target Directory")
        if directory:
            self.selected_directory = directory
            self.lbl_current_dir_display.setText(f"📍 Active Monitoring Zone:\n{directory}")
            self.lbl_status.setText(f"Target selected: {Path(directory).name}")
            self.switch_page(1) # Send user straight to scanner visual workspace
            self.scan_folder()

    def scan_folder(self):
        if not self.selected_directory:
            return
            
        self.scanned_files.clear()
        self.table_files.setRowCount(0)
        self.pending_moves.clear()
        
        try:
            # Safe linear directory scanning avoiding deep recursions
            with os.scandir(self.selected_directory) as entries:
                for entry in entries:
                    if entry.is_file():
                        file_path = Path(entry.path)
                        size_kb = round(entry.stat().st_size / 1024, 2)
                        ext = file_path.suffix.lower()
                        
                        file_info = {
                            'name': entry.name,
                            'path': entry.path,
                            'size': size_kb,
                            'ext': ext
                        }
                        self.scanned_files.append(file_info)
                        
            # Populate UI Data Table Grid
            self.table_files.setRowCount(len(self.scanned_files))
            for row, file_info in enumerate(self.scanned_files):
                self.table_files.setItem(row, 0, QTableWidgetItem(file_info['name']))
                self.table_files.setItem(row, 1, QTableWidgetItem(str(file_info['size'])))
                self.table_files.setItem(row, 2, QTableWidgetItem(file_info['ext'] if file_info['ext'] else "Unknown"))
                
                # Default status state item
                rec_item = QTableWidgetItem("Awaiting Analysis Pipeline")
                rec_item.setForeground(QColor("#AAAAAA"))
                self.table_files.setItem(row, 3, rec_item)

            if self.scanned_files:
                self.btn_ai_organize.setEnabled(True)
                self.lbl_status.setText(f"Scan complete: Loaded {len(self.scanned_files)} files.")
            else:
                self.lbl_status.setText("Target directory clean or empty.")
                self.btn_ai_organize.setEnabled(False)
                
        except Exception as e:
            QMessageBox.critical(self, "Hardware Engine Error", f"Failed accessing directory paths:\n{str(e)}")

    def generate_ai_organization_preview(self):
        """ Simulates deep classification model parsing mapping transformations before applying updates """
        if not self.scanned_files:
            return

        self.pending_moves.clear()
        
        for row in range(self.table_files.rowCount()):
            file_name = self.table_files.item(row, 0).text()
            ext = self.table_files.item(row, 2).text()
            
            # Match rules using engine mapping
            target_folder = "Unsorted"
            for category, extensions in self.extension_map.items():
                if ext in extensions:
                    target_folder = category
                    break
                    
            # Prevent sorting already cleanly sorted folders inside workspace
            src_path = Path(self.selected_directory) / file_name
            dest_dir = Path(self.selected_directory) / target_folder
            dest_path = dest_dir / file_name
            
            if target_folder != "Unsorted":
                self.pending_moves.append({'src': src_path, 'dest_dir': dest_dir, 'dest': dest_path})
                preview_item = QTableWidgetItem(f"🚚 Move to [ /{target_folder} ]")
                preview_item.setForeground(QColor("#00E5FF")) # UI Neon Blueprint Blue
            else:
                preview_item = QTableWidgetItem("⚠️ Leave Unchanged (Unknown Extension)")
                preview_item.setForeground(QColor("#FFCC00"))
                
            self.table_files.setItem(row, 3, preview_item)

        # Execution prompt trigger
        if self.pending_moves:
            reply = QMessageBox.question(
                self, 'AI Optimization Plan Ready',
                f"The Engine analyzed raw vectors and generated {len(self.pending_moves)} smart category path transforms.\n\nExecute deployment safely?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.execute_organization()
        else:
            QMessageBox.information(self, "Analysis Matrix Verdict", "Directory files are perfectly optimized already.")

    def execute_organization(self):
        """ Commits file sorting system moves safely using clean transactions and handling path name collisions """
        executed_transactions = []
        
        try:
            for transaction in self.pending_moves:
                src_path = Path(transaction['src'])
                dest_dir = Path(transaction['dest_dir'])
                dest_path = Path(transaction['dest'])
                
                # Check file existence check protection edge states
                if not src_path.exists():
                    continue
                    
                # Create parent category subdirectory path lazily
                dest_dir.mkdir(exist_ok=True)
                
                # Handle File Hash / Path Name Name Collisions safely dynamically
                if dest_path.exists():
                    base_name = dest_path.stem
                    suffix = dest_path.suffix
                    counter = 1
                    while dest_path.exists():
                        dest_path = dest_dir / f"{base_name}_{counter}{suffix}"
                        counter += 1

                # Core operational file move execution
                shutil.move(str(src_path), str(dest_path))
                executed_transactions.append({'src': src_path, 'actual_dest': dest_path})
                
            # Log for active Undo Operations State Rollback
            if executed_transactions:
                self.history_log.append(executed_transactions)
                self.btn_undo.setEnabled(True)
                self.lbl_stat_counter.setText(f"Files Sorted Safely: {len(executed_transactions)}\nLast Result: Success")
                QMessageBox.information(self, "System Update Matrix", f"Cleaned and moved {len(executed_transactions)} files successfully!")
            
            # Recalibrate view updates
            self.scan_folder()
            
        except Exception as e:
            QMessageBox.critical(self, "Operational Pipeline Interrupted", f"Failed performing file structural movements:\n{str(e)}")

    def undo_last_action(self):
        """ Implements structural software stack state restoration via Command Design Patterns rollback """
        if not self.history_log:
            return
            
        last_action_batch = self.history_log.pop()
        rollback_counter = 0
        
        try:
            for item in reversed(last_action_batch):
                current_location = Path(item['actual_dest'])
                original_location = Path(item['src'])
                
                if current_location.exists():
                    shutil.move(str(current_location), str(original_location))
                    rollback_counter += 1
                    
            self.lbl_status.setText(f"Undo system rollback completed: {rollback_counter} files tracking profiles reverted.")
            
            if not self.history_log:
                self.btn_undo.setEnabled(False)
                
            # Re-read workspace status transformations
            self.scan_folder()
            QMessageBox.information(self, "System Reversion Safe", f"Successfully reversed {rollback_counter} paths back into original positions.")
            
        except Exception as e:
            QMessageBox.critical(self, "Rollback Protection Fault", f"Error restoring original folder structures:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartFileManager()
    window.show()
    sys.exit(app.exec())