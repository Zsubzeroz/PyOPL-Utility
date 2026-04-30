import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
    QFileDialog, QLabel, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt

from core.splitter import split_iso
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QProgressDialog

class SplitterWorker(QThread):
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, iso_path, usb_root, game_id, name):
        super().__init__()
        self.iso_path = iso_path
        self.usb_root = usb_root
        self.game_id = game_id
        self.name = name
        
    def run(self):
        try:
            split_iso(self.iso_path, self.usb_root, self.game_id, self.name, self.report_progress)
            self.finished.emit(True, "Splitting e ul.cfg concluídos com sucesso!")
        except Exception as e:
            self.finished.emit(False, str(e))
            
    def report_progress(self, copied, total):
        self.progress.emit(copied, total)

class PyOPLMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyOPL Utility")
        self.resize(950, 600)
        
        self.current_directory = ""
        self.iso_files = []
        
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # --- Top bar ---
        top_layout = QHBoxLayout()
        self.dir_label = QLabel("Diretório: Nenhum selecionado")
        self.dir_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        btn_browse = QPushButton("Procurar Pasta...")
        btn_browse.clicked.connect(self.browse_directory)
        btn_scan = QPushButton("Analisar Pasta Atual")
        btn_scan.clicked.connect(self.scan_directory)
        
        top_layout.addWidget(self.dir_label, stretch=1)
        top_layout.addWidget(btn_browse)
        top_layout.addWidget(btn_scan)
        
        main_layout.addLayout(top_layout)
        
        # --- Table ---
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "Arquivo Original", "Game ID", "Nome Limpo", "Tamanho (GB)", "Status"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.table)
        
        # --- Bottom bar ---
        bottom_layout = QHBoxLayout()
        btn_rename = QPushButton("Renomear Selecionados (OPL)")
        btn_rename.clicked.connect(self.rename_selected)
        btn_rename.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold;")
        
        btn_split = QPushButton("Dividir ISOs (>4GB) para FAT32")
        btn_split.clicked.connect(self.split_selected)
        btn_split.setStyleSheet("background-color: #0277bd; color: white; font-weight: bold;")
        
        btn_art = QPushButton("Baixar Capas [Em Breve]")
        btn_art.setEnabled(False)
        
        bottom_layout.addWidget(btn_rename)
        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_split)
        bottom_layout.addWidget(btn_art)
        
        main_layout.addLayout(bottom_layout)
        
        # --- Signature ---
        footer_label = QLabel("Software de Uso Livre | Idealizado e disponibilizado por Luan Estifer R. Pereira (Zsubzeroz)")
        footer_label.setStyleSheet("color: gray; font-style: italic; font-size: 11px; margin-top: 5px;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(footer_label)
        
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Selecione a pasta com as ISOs de PS2")
        if directory:
            self.current_directory = directory
            self.dir_label.setText(f"Diretório: {self.current_directory}")
            self.scan_directory()
            
    def scan_directory(self):
        if not self.current_directory or not os.path.exists(self.current_directory):
            return
            
        self.table.setRowCount(0)
        self.iso_files = []
        
        try:
            files = [f for f in os.listdir(self.current_directory) if f.lower().endswith('.iso')]
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível ler o diretório:\n{e}")
            return
            
        for row, filename in enumerate(files):
            filepath = os.path.join(self.current_directory, filename)
            size_gb = os.path.getsize(filepath) / (1024**3)
            
            game_id = get_game_id_from_iso(filepath)
            
            clean_name = filename
            status = "Pronto"
            
            if game_id:
                if filename.startswith(game_id + '.'):
                    clean_name = filename[len(game_id)+1:-4]
                else:
                    status = "Precisa Renomear"
            else:
                game_id = "N/A"
                status = "ID Não Encontrado"
                
            if size_gb > 4.0:
                status += " | Arquivo > 4GB"
                
            self.iso_files.append({
                "filepath": filepath,
                "game_id": game_id,
                "status": status,
                "filename": filename,
                "clean_name": clean_name
            })
            
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(filename))
            self.table.setItem(row, 1, QTableWidgetItem(game_id))
            self.table.setItem(row, 2, QTableWidgetItem(clean_name))
            self.table.setItem(row, 3, QTableWidgetItem(f"{size_gb:.2f}"))
            
            status_item = QTableWidgetItem(status)
            if "Precisa Renomear" in status:
                status_item.setForeground(Qt.GlobalColor.darkYellow)
            elif "ID Não Encontrado" in status:
                status_item.setForeground(Qt.GlobalColor.red)
            else:
                status_item.setForeground(Qt.GlobalColor.darkGreen)
                
            self.table.setItem(row, 4, status_item)

    def rename_selected(self):
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            QMessageBox.information(self, "Aviso", "Selecione pelo menos um jogo na tabela para renomear.")
            return
            
        success_count = 0
        error_count = 0
        
        for row in selected_rows:
            data = self.iso_files[row]
            if data["game_id"] != "N/A" and "Precisa Renomear" in data["status"]:
                try:
                    rename_iso_for_opl(data["filepath"], data["game_id"])
                    success_count += 1
                except Exception as e:
                    print(f"Error renaming {data['filename']}: {e}")
                    error_count += 1
                    
        msg = f"{success_count} jogos renomeados com sucesso!"
        if error_count > 0:
            msg += f"\n{error_count} erros ao renomear (verifique o console)."
            
        QMessageBox.information(self, "Resultado", msg)
        self.scan_directory() # Refresh

    def split_selected(self):
        selected_rows = list(set(item.row() for item in self.table.selectedItems()))
        if not selected_rows:
            QMessageBox.information(self, "Aviso", "Selecione pelo menos um jogo na tabela para dividir.")
            return
            
        if len(selected_rows) > 1:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione apenas UM jogo de cada vez para dividir.")
            return
            
        data = self.iso_files[selected_rows[0]]
        if data["game_id"] == "N/A":
            QMessageBox.warning(self, "Erro", "Não é possível dividir um jogo sem o Game ID extraído.")
            return
            
        usb_root = QFileDialog.getExistingDirectory(self, "Selecione a RAIZ do seu Pendrive FAT32")
        if not usb_root:
            return
            
        # UI de Progresso
        self.progress_dialog = QProgressDialog(f"Copiando {data['clean_name']}...", "Cancelar", 0, 100, self)
        self.progress_dialog.setWindowTitle("Aguarde")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setAutoReset(True)
        self.progress_dialog.setValue(0)
        
        self.worker = SplitterWorker(data["filepath"], usb_root, data["game_id"], data["clean_name"])
        
        def update_progress(copied, total):
            percent = int((copied / total) * 100)
            self.progress_dialog.setValue(percent)
            if self.progress_dialog.wasCanceled():
                self.worker.terminate()
                
        def on_finished(success, msg):
            if success:
                QMessageBox.information(self, "Sucesso", msg)
            else:
                QMessageBox.critical(self, "Erro", f"Falha na cópia: {msg}")
                
        self.worker.progress.connect(update_progress)
        self.worker.finished.connect(on_finished)
        self.worker.start()
        self.progress_dialog.show()
