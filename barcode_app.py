import sys
import csv
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox, 
                            QSpinBox, QFileDialog, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QKeyEvent, QFont

class BarcodeScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("条码扫描截取工具")
        self.setGeometry(100, 100, 800, 600)
        self.settings = QSettings("BarcodeTools", "ScannerApp")
        
        # 应用默认设置
        self.start_pos = self.settings.value("start_pos", 0, type=int)
        self.length = self.settings.value("length", 6, type=int)
        self.auto_save = self.settings.value("auto_save", False, type=bool)
        self.output_dir = self.settings.value("output_dir", os.path.expanduser("~"), type=str)
        
        self.init_ui()
        self.scan_history = []
        
        # 设置焦点以便接收键盘输入
        self.setFocusPolicy(Qt.StrongFocus)
        
    def init_ui(self):
        # 创建主布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 设置区域
        settings_group = QGroupBox("截取设置")
        settings_layout = QHBoxLayout()
        
        # 起始位置设置
        start_layout = QVBoxLayout()
        start_layout.addWidget(QLabel("起始位置:"))
        self.start_spin = QSpinBox()
        self.start_spin.setRange(0, 100)
        self.start_spin.setValue(self.start_pos)
        self.start_spin.valueChanged.connect(self.save_settings)
        start_layout.addWidget(self.start_spin)
        
        # 截取长度设置
        length_layout = QVBoxLayout()
        length_layout.addWidget(QLabel("截取长度:"))
        self.length_spin = QSpinBox()
        self.length_spin.setRange(1, 100)
        self.length_spin.setValue(self.length)
        self.length_spin.valueChanged.connect(self.save_settings)
        length_layout.addWidget(self.length_spin)
        
        # 自动保存设置
        auto_save_layout = QVBoxLayout()
        self.auto_save_check = QCheckBox("自动保存扫描记录")
        self.auto_save_check.setChecked(self.auto_save)
        self.auto_save_check.stateChanged.connect(self.save_settings)
        auto_save_layout.addWidget(self.auto_save_check)
        
        # 添加到设置区域
        settings_layout.addLayout(start_layout)
        settings_layout.addLayout(length_layout)
        settings_layout.addLayout(auto_save_layout)
        settings_layout.addStretch()
        settings_group.setLayout(settings_layout)
        
        # 输入区域
        input_group = QGroupBox("扫码输入")
        input_layout = QVBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("请用扫码枪扫描条码...")
        self.input_field.setReadOnly(True)
        self.input_field.setFont(QFont("Arial", 16))
        input_layout.addWidget(self.input_field)
        
        input_group.setLayout(input_layout)
        
        # 结果显示区域
        result_group = QGroupBox("扫描结果")
        result_layout = QVBoxLayout()
        
        self.result_field = QTextEdit()
        self.result_field.setReadOnly(True)
        self.result_field.setFont(QFont("Consolas", 12))
        result_layout.addWidget(self.result_field)
        
        result_group.setLayout(result_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("清空记录")
        self.clear_btn.clicked.connect(self.clear_history)
        button_layout.addWidget(self.clear_btn)
        
        self.export_btn = QPushButton("导出数据")
        self.export_btn.clicked.connect(self.export_data)
        button_layout.addWidget(self.export_btn)
        
        self.copy_btn = QPushButton("复制结果")
        self.copy_btn.clicked.connect(self.copy_result)
        button_layout.addWidget(self.copy_btn)
        
        # 添加到主布局
        main_layout.addWidget(settings_group)
        main_layout.addWidget(input_group)
        main_layout.addWidget(result_group)
        main_layout.addLayout(button_layout)
        
        # 状态栏
        self.statusBar().showMessage("就绪 | 使用扫码枪扫描条码")
        
    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘输入事件（扫码枪输入）"""
        # 忽略功能键和控制键
        if event.key() in [Qt.Key_Shift, Qt.Key_Control, Qt.Key_Alt, Qt.Key_Meta]:
            return
        
        # 处理回车键（表示一次扫描完成）
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            barcode = self.input_field.text().strip()
            if barcode:
                self.process_barcode(barcode)
            self.input_field.clear()
            return
        
        # 处理普通按键
        if event.text():
            current_text = self.input_field.text()
            self.input_field.setText(current_text + event.text())
        
    def process_barcode(self, barcode):
        """处理扫描到的条码"""
        # 获取截取设置
        start = self.start_spin.value()
        length = self.length_spin.value()
        
        # 执行截取
        if start < len(barcode):
            extracted = barcode[start:start+length]
        else:
            extracted = ""
        
        # 创建时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 添加到历史记录
        self.scan_history.append({
            "timestamp": timestamp,
            "original": barcode,
            "extracted": extracted,
            "start": start,
            "length": length
        })
        
        # 更新结果展示
        self.update_result_display()
        
        # 自动保存
        if self.auto_save_check.isChecked():
            self.save_to_file(extracted)
        
        # 状态栏提示
        self.statusBar().showMessage(f"已处理条码: {barcode} -> {extracted}")
    
    def update_result_display(self):
        """更新结果展示区域"""
        self.result_field.clear()
        
        # 添加表头
        header = f"{'时间':<20} {'原始条码':<25} {'截取结果':<15} {'位置':<10} {'长度':<6}\n"
        self.result_field.append(header)
        self.result_field.append("-" * 80)
        
        # 添加历史记录（从最新到最旧）
        for record in reversed(self.scan_history):
            line = (f"{record['timestamp']:<20} "
                    f"{record['original']:<25} "
                    f"{record['extracted']:<15} "
                    f"{record['start']:<10} "
                    f"{record['length']:<6}")
            self.result_field.append(line)
    
    def clear_history(self):
        """清空历史记录"""
        if not self.scan_history:
            return
            
        reply = QMessageBox.question(self, "确认清空", 
                                    "确定要清空所有扫描记录吗？",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.scan_history = []
            self.result_field.clear()
            self.statusBar().showMessage("扫描记录已清空")
    
    def export_data(self):
        """导出数据到CSV文件"""
        if not self.scan_history:
            QMessageBox.warning(self, "无数据", "没有可导出的扫描记录")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出扫描数据", 
            os.path.join(self.output_dir, "barcode_data.csv"),
            "CSV文件 (*.csv)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # 写入表头
                writer.writerow(["时间", "原始条码", "截取结果", "起始位置", "截取长度"])
                
                # 写入数据
                for record in self.scan_history:
                    writer.writerow([
                        record['timestamp'],
                        record['original'],
                        record['extracted'],
                        record['start'],
                        record['length']
                    ])
            
            self.output_dir = os.path.dirname(file_path)
            self.save_settings()
            self.statusBar().showMessage(f"数据已导出到: {file_path}")
            QMessageBox.information(self, "导出成功", f"成功导出 {len(self.scan_history)} 条记录")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出数据时出错:\n{str(e)}")
    
    def copy_result(self):
        """复制当前截取结果到剪贴板"""
        if not self.scan_history:
            return
            
        # 获取最新结果
        latest = self.scan_history[-1]['extracted']
        clipboard = QApplication.clipboard()
        clipboard.setText(latest)
        self.statusBar().showMessage(f"已复制: {latest}")
    
    def save_to_file(self, content):
        """自动保存扫描结果到文件"""
        file_path = os.path.join(self.output_dir, "barcode_log.txt")
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp}\t{content}\n")
        except Exception as e:
            self.statusBar().showMessage(f"自动保存失败: {str(e)}")
    
    def save_settings(self):
        """保存应用设置"""
        self.settings.setValue("start_pos", self.start_spin.value())
        self.settings.setValue("length", self.length_spin.value())
        self.settings.setValue("auto_save", self.auto_save_check.isChecked())
        self.settings.setValue("output_dir", self.output_dir)
    
    def closeEvent(self, event):
        """关闭窗口时保存设置"""
        self.save_settings()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = BarcodeScannerApp()
    window.show()
    sys.exit(app.exec_())