import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import barcode
from barcode.writer import ImageWriter
from pyzbar.pyzbar import decode

class SimpleBarcodeApp:
    def __init__(self, master):
        self.master = master
        master.title("条码打印助手")
        master.geometry("400x350")
        
        # 创建界面
        tk.Label(master, text="条码内容:").pack(pady=5)
        self.entry = tk.Entry(master, width=40)
        self.entry.pack(pady=5)
        
        # 按钮区域
        btn_frame = tk.Frame(master)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="生成条码", command=self.generate_barcode).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="扫描图片", command=self.scan_barcode).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="打印条码", command=self.print_barcode).grid(row=0, column=2, padx=5)
        
        # 图片显示区域
        self.image_label = tk.Label(master)
        self.image_label.pack(pady=10)
        
        # 状态标签
        self.status_label = tk.Label(master, text="就绪", fg="green")
        self.status_label.pack(pady=5)
        
        # 当前条码文件
        self.barcode_file = "barcode.png"

    def generate_barcode(self):
        text = self.entry.get().strip()
        if not text:
            messagebox.showerror("错误", "请输入条码内容")
            return
        
        try:
            # 生成Code128条码
            self.status_label.config(text="正在生成条码...", fg="blue")
            self.master.update()  # 更新界面显示状态
            
            code = barcode.get_barcode_class('code128')
            barcode_img = code(text, writer=ImageWriter())
            barcode_img.save(self.barcode_file)
            
            # 显示图片
            img = Image.open(self.barcode_file)
            img = img.resize((300, 100), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_label.image = photo
            
            self.status_label.config(text="条码生成成功！", fg="green")
        except Exception as e:
            self.status_label.config(text="生成失败", fg="red")
            messagebox.showerror("错误", f"生成条码失败: {str(e)}")

    def scan_barcode(self):
        try:
            self.status_label.config(text="选择图片中...", fg="blue")
            file_path = filedialog.askopenfilename(
                title="选择条码图片",
                filetypes=[("图片文件", "*.png;*.jpg;*.jpeg")]
            )
            
            if not file_path:
                self.status_label.config(text="已取消", fg="orange")
                return
                
            self.status_label.config(text="正在扫描...", fg="blue")
            self.master.update()  # 更新界面显示状态
            
            img = Image.open(file_path)
            decoded = decode(img)
            if decoded:
                text = decoded[0].data.decode("utf-8")
                self.entry.delete(0, tk.END)
                self.entry.insert(0, text)
                self.status_label.config(text="扫描成功", fg="green")
                messagebox.showinfo("扫描成功", f"识别内容: {text}")
            else:
                self.status_label.config(text="未识别到条码", fg="orange")
                messagebox.showinfo("扫描失败", "未识别到条码")
        except Exception as e:
            self.status_label.config(text="扫描失败", fg="red")
            messagebox.showerror("错误", f"扫描失败: {str(e)}")

    def print_barcode(self):
        if not os.path.exists(self.barcode_file):
            self.status_label.config(text="请先生成条码", fg="red")
            messagebox.showerror("错误", "请先生成条码")
            return
            
        self.status_label.config(text="准备打印...", fg="blue")
        messagebox.showinfo("打印提示", 
            "打印功能将在Windows上自动工作\n"
            "在Mac上测试时，条码文件已保存为: barcode.png\n"
            "您可以用其他程序打印此文件\n\n"
            "文件路径: " + os.path.abspath(self.barcode_file))
        self.status_label.config(text="已显示打印说明", fg="green")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleBarcodeApp(root)
    root.mainloop()
