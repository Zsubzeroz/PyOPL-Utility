import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
    QFileDialog, QLabel, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt

from core.splitter import split_iso, copy_iso_intact
from core.iso_handler import get_game_id_from_iso
from core.renamer import rename_iso_for_opl
from core.art_downloader import download_arts
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QProgressDialog

class DownloaderWorker(QThread):
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(int, int)
    
    def __init__(self, iso_files_list, usb_root):
        super().__init__()
        self.iso_files_list = iso_files_list
        self.usb_root = usb_root
        
    def run(self):
        success, error = download_arts(self.iso_files_list, self.usb_root, self.report_progress)
        self.finished.emit(success, error)
        
    def report_progress(self, current, total, status_msg):
        self.progress.emit(current, total, status_msg)

class TransferWorker(QThread):
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, iso_path, usb_root, game_id, name, size_gb):
        super().__init__()
        self.iso_path = iso_path
        self.usb_root = usb_root
        self.game_id = game_id
        self.name = name
        self.size_gb = size_gb
        
    def run(self):
        import shutil
        try:
            total, used, free = shutil.disk_usage(self.usb_root)
            file_size = os.path.getsize(self.iso_path)
            
            # Adiciona uma margem de segurança de 10MB para metadados/arquivos extras
            if free < (file_size + 10 * 1024 * 1024):
                self.finished.emit(False, f"Espaço insuficiente no pendrive!\nLivre: {free / (1024**3):.2f} GB\nNecessário: {file_size / (1024**3):.2f} GB")
                return
                
            if self.size_gb > 4.0:
                split_iso(self.iso_path, self.usb_root, self.game_id, self.name, self.report_progress)
                self.finished.emit(True, "Transferência (Dividido) e ul.cfg concluídos com sucesso!")
            else:
                copy_iso_intact(self.iso_path, self.usb_root, self.game_id, self.name, self.report_progress)
                self.finished.emit(True, "Transferência (Cópia Direta DVD/CD) concluída com sucesso!")

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
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed)
        self.table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.table)
        
        # --- Bottom bar ---
        bottom_layout = QHBoxLayout()
        btn_rename = QPushButton("Renomear Selecionados (OPL)")
        btn_rename.clicked.connect(self.rename_selected)
        btn_rename.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold;")
        
        btn_transfer = QPushButton("Transferir Selecionado (USB)")
        btn_transfer.clicked.connect(self.transfer_selected)
        btn_transfer.setStyleSheet("background-color: #0277bd; color: white; font-weight: bold;")
        
        self.btn_art = QPushButton("Baixar Capas")
        self.btn_art.clicked.connect(self.download_arts_selected)
        self.btn_art.setStyleSheet("background-color: #f57c00; color: white; font-weight: bold;")
        
        bottom_layout.addWidget(btn_rename)
        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_transfer)
        bottom_layout.addWidget(self.btn_art)
        
        main_layout.addLayout(bottom_layout)
        
        # --- Signature ---
        footer_label = QLabel("Software de Uso Livre | Idealizado e disponibilizado por Luan Estifer R. Pereira (Zsubzeroz)")
        footer_label.setStyleSheet("color: gray; font-style: italic; font-size: 11px; margin-top: 5px;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(footer_label)
        
    def browse_directory(self):
        options = QFileDialog.Option.DontUseNativeDialog
        directory = QFileDialog.getExistingDirectory(self, "Selecione a pasta com as ISOs de PS2", options=options)
        if directory:
            self.current_directory = directory
            self.dir_label.setText(f"Diretório: {self.current_directory}")
            self.scan_directory()
            
    def scan_directory(self):
        try:
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
                    "clean_name": clean_name,
                    "size_gb": size_gb
                })
                
                self.table.insertRow(row)
                
                item_filename = QTableWidgetItem(filename)
                item_filename.setFlags(item_filename.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 0, item_filename)
                
                item_id = QTableWidgetItem(game_id)
                item_id.setFlags(item_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 1, item_id)
                
                item_clean = QTableWidgetItem(clean_name)
                # Allow editing 'Nome Limpo'
                item_clean.setFlags(item_clean.flags() | Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 2, item_clean)
                
                item_size = QTableWidgetItem(f"{size_gb:.2f}")
                item_size.setFlags(item_size.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 3, item_size)
                
                status_item = QTableWidgetItem(status)
                status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if "Precisa Renomear" in status:
                    status_item.setForeground(Qt.GlobalColor.darkYellow)
                elif "ID Não Encontrado" in status:
                    status_item.setForeground(Qt.GlobalColor.red)
                else:
                    status_item.setForeground(Qt.GlobalColor.darkGreen)
                    
                self.table.setItem(row, 4, status_item)
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Fatal Error", f"Traceback:\n{traceback.format_exc()}")

    def rename_selected(self):
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            QMessageBox.information(self, "Aviso", "Selecione pelo menos um jogo na tabela para renomear.")
            return
            
        success_count = 0
        error_count = 0
        
        for row in selected_rows:
            data = self.iso_files[row]
            
            # Fetch the potentially edited name from the table
            item_clean = self.table.item(row, 2)
            custom_name = item_clean.text().strip() if item_clean else data["clean_name"]
            
            # If status is "Pronto" but the user changed the name, they might want to rename it anyway.
            # But the original logic was checking for "Precisa Renomear".
            # We will allow renaming if it has a Game ID.
            if data["game_id"] != "N/A":
                try:
                    new_path = rename_iso_for_opl(data["filepath"], data["game_id"], custom_name)
                    if new_path != data["filepath"]:
                        success_count += 1
                except Exception as e:
                    error_count += 1
                    
        msg = f"{success_count} jogos renomeados com sucesso!"
        if error_count > 0:
            msg += f"\n{error_count} erros ao renomear (verifique o console)."
            
        QMessageBox.information(self, "Resultado", msg)
        self.scan_directory() # Refresh

    def transfer_selected(self):
        selected_rows = list(set(item.row() for item in self.table.selectedItems()))
        if not selected_rows:
            QMessageBox.information(self, "Aviso", "Selecione pelo menos um jogo na tabela para transferir.")
            return
            
        if len(selected_rows) > 1:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione apenas UM jogo de cada vez para transferir.")
            return
            
        data = self.iso_files[selected_rows[0]]
        
        # Fetch the potentially edited name from the table
        item_clean = self.table.item(selected_rows[0], 2)
        custom_name = item_clean.text().strip() if item_clean else data["clean_name"]
        
        # If the user still hasn't provided a name, fallback to game_id
        if not custom_name:
            custom_name = data["game_id"]
            
        if data["game_id"] == "N/A":
            QMessageBox.warning(self, "Erro", "Não é possível dividir um jogo sem o Game ID extraído.")
            return
            
        from core.usb_detector import detect_usb_drives
        from PyQt6.QtWidgets import QInputDialog
        
        detected_drives = detect_usb_drives()
        usb_root = None
        
        if detected_drives:
            items = [d['name'] for d in detected_drives]
            items.append("Outro lugar... (Procurar Manualmente)")
            
            item, ok = QInputDialog.getItem(self, "Selecionar Pendrive", 
                                            "Os seguintes dispositivos foram encontrados:", items, 0, False)
            if ok and item:
                if item == "Outro lugar... (Procurar Manualmente)":
                    options = QFileDialog.Option.DontUseNativeDialog
                    usb_root = QFileDialog.getExistingDirectory(self, "Selecione a RAIZ do seu Pendrive FAT32", options=options)
                else:
                    # Encontrar o path correspondente
                    for d in detected_drives:
                        if d['name'] == item:
                            usb_root = d['path']
                            break
            else:
                return # User cancelled
        else:
            reply = QMessageBox.question(self, "Nenhum USB Detectado", 
                                         "Não detectei nenhum pendrive conectado.\nDeseja procurar a pasta manualmente?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                options = QFileDialog.Option.DontUseNativeDialog
                usb_root = QFileDialog.getExistingDirectory(self, "Selecione a RAIZ do seu Pendrive FAT32", options=options)
            else:
                return
                
        if not usb_root:
            return
            
        # UI de Progresso
        self.progress_dialog = QProgressDialog(f"Copiando {custom_name}...", "Cancelar", 0, 100, self)
        self.progress_dialog.setWindowTitle("Aguarde")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setAutoReset(True)
        self.progress_dialog.setValue(0)
        
        self.worker = TransferWorker(data["filepath"], usb_root, data["game_id"], custom_name, data["size_gb"])
        
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

    def download_arts_selected(self):
        selected_rows = list(set(item.row() for item in self.table.selectedItems()))
        if not selected_rows:
            QMessageBox.information(self, "Aviso", "Selecione pelo menos um jogo na tabela para baixar a capa.")
            return
            
        from core.usb_detector import detect_usb_drives
        from PyQt6.QtWidgets import QInputDialog
        
        detected_drives = detect_usb_drives()
        usb_root = None
        
        if detected_drives:
            items = [d['name'] for d in detected_drives]
            items.append("Outro lugar... (Procurar Manualmente)")
            
            item, ok = QInputDialog.getItem(self, "Onde salvar as capas?", 
                                            "Selecione o Pendrive (A pasta ART será criada nele):", items, 0, False)
            if ok and item:
                if item == "Outro lugar... (Procurar Manualmente)":
                    options = QFileDialog.Option.DontUseNativeDialog
                    usb_root = QFileDialog.getExistingDirectory(self, "Selecione a RAIZ do seu Pendrive FAT32", options=options)
                else:
                    for d in detected_drives:
                        if d['name'] == item:
                            usb_root = d['path']
                            break
            else:
                return
        else:
            options = QFileDialog.Option.DontUseNativeDialog
            usb_root = QFileDialog.getExistingDirectory(self, "Selecione a RAIZ do seu Pendrive FAT32", options=options)
            
        if not usb_root:
            return
            
        games_to_download = [self.iso_files[row] for row in selected_rows]
        
        self.art_progress = QProgressDialog("Baixando capas...", "Cancelar", 0, len(games_to_download), self)
        self.art_progress.setWindowTitle("Aguarde")
        self.art_progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.art_progress.setAutoClose(True)
        self.art_progress.setAutoReset(True)
        self.art_progress.setValue(0)
        
        self.art_worker = DownloaderWorker(games_to_download, usb_root)
        
        def update_art_progress(current, total, msg):
            self.art_progress.setLabelText(f"Baixando: {msg}")
            self.art_progress.setValue(current)
            if self.art_progress.wasCanceled():
                self.art_worker.terminate()
                
        def on_art_finished(success, error):
            QMessageBox.information(self, "Downloads Concluídos", f"Capas baixadas com sucesso: {success}\nFalhas: {error}")
            
        self.art_worker.progress.connect(update_art_progress)
        self.art_worker.finished.connect(on_art_finished)
        self.art_worker.start()
        self.art_progress.show()
