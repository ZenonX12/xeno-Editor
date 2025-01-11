import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import sys
import io
import keyword
import tkinter.simpledialog
import os
import time
import requests  # For making HTTP requests

# GitHub repository URL for checking updates
GITHUB_API_URL = "https://github.com/ZenonX12/xeno-Editor"

# ฟังก์ชันสำหรับเมนู
def show_message():
    messagebox.showinfo("About Xeno Editor", 
                        "Xeno Editor\nVersion 1.0.0 Beta Test\n\nA simple text editor built with Tkinter.\nCreated by Xeno.")

# ฟังก์ชันสำหรับแสดงข้อความใน Text widget
def display_code():
    code_text.insert(tk.END, "# ใส่โค้ดของคุณที่นี่\n")
    code_text.insert(tk.END, "print('Hello, World!')\n")

# ฟังก์ชันสำหรับเปิดไฟล์
def open_file():
    file_path = filedialog.askopenfilename(title="เลือกไฟล์", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                code_text.delete(1.0, tk.END)  # ลบข้อความเก่าใน Text widget
                code_text.insert(tk.END, content)  # แสดงเนื้อหาของไฟล์ใน Text widget
                highlight_code(content)
        except UnicodeDecodeError:
            messagebox.showerror("Error", "ไม่สามารถอ่านไฟล์ได้เนื่องจากปัญหาการเข้ารหัส")
            log_error("UnicodeDecodeError: Could not read file due to encoding issue.")
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {e}")
            log_error(f"Exception: {str(e)}")

# ฟังก์ชันสำหรับบันทึกไฟล์
def save_file():
    file_path = filedialog.asksaveasfilename(title="บันทึกไฟล์", defaultextension=".txt", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                content = code_text.get(1.0, tk.END)  # รับข้อความจาก Text widget
                file.write(content)  # บันทึกเนื้อหาลงในไฟล์
                messagebox.showinfo("Save", "บันทึกไฟล์สำเร็จ")
        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {e}")
            log_error(f"Exception: {str(e)}")

# ฟังก์ชันสำหรับการรันโค้ด
def run_code():
    code = code_text.get(1.0, tk.END)  # รับโค้ดจาก Text widget

    # รีไดเรกต์เอาต์พุตไปยัง Text widget
    output = io.StringIO()
    sys.stdout = output

    try:
        exec(code)  # รันโค้ด
    except Exception as e:
        error_message = f"Error at line {e.__traceback__.tb_lineno}: {str(e)}"
        messagebox.showerror("Error", error_message)
        log_error(f"Error at line {e.__traceback__.tb_lineno}: {str(e)}")
    else:
        # แสดงผลลัพธ์ใน Text widget
        result = output.getvalue()
        code_text.insert(tk.END, "\n\n# ผลลัพธ์:\n")
        code_text.insert(tk.END, result)
    finally:
        # รีเซ็ตการรีไดเรกต์เอาต์พุต
        sys.stdout = sys.__stdout__

# ฟังก์ชันสำหรับการเน้นสีซินแท็กซ์ (Highlighting)
def highlight_code(content):
    # Remove all previous tags
    code_text.tag_remove("keyword", "1.0", tk.END)
    code_text.tag_remove("string", "1.0", tk.END)
    code_text.tag_remove("comment", "1.0", tk.END)
    code_text.tag_remove("number", "1.0", tk.END)

    # Highlight keywords
    for word in keyword.kwlist:
        start_idx = '1.0'
        while True:
            start_idx = code_text.search(rf"\b{word}\b", start_idx, stopindex=tk.END, regexp=True)
            if not start_idx:
                break
            end_idx = f"{start_idx}+{len(word)}c"
            code_text.tag_add("keyword", start_idx, end_idx)
            start_idx = end_idx

    code_text.tag_configure("keyword", foreground="#569cd6")  # Keyword color

    # Highlight strings (double or single quotes)
    start_idx = '1.0'
    while True:
        start_idx = code_text.search(r"(['\"].*?['\"])|(['\"]).*?['\"]", start_idx, stopindex=tk.END, regexp=True)
        if not start_idx:
            break
        end_idx = f"{start_idx}+{len(code_text.get(start_idx, f'{start_idx}+200c'))}c"
        code_text.tag_add("string", start_idx, end_idx)
        start_idx = end_idx

    code_text.tag_configure("string", foreground="#6a9955")  # String color

    # Highlight comments (assuming Python-style comments)
    start_idx = '1.0'
    while True:
        start_idx = code_text.search(r"#.*", start_idx, stopindex=tk.END)
        if not start_idx:
            break
        end_idx = code_text.index(f"{start_idx}+{len(code_text.get(start_idx, f'{start_idx}+200c'))}c")
        code_text.tag_add("comment", start_idx, end_idx)
        start_idx = end_idx

    code_text.tag_configure("comment", foreground="#808080")  # Comment color

    # Highlight numbers
    start_idx = '1.0'
    while True:
        start_idx = code_text.search(r"\b\d+\b", start_idx, stopindex=tk.END)
        if not start_idx:
            break
        end_idx = f"{start_idx}+{len(code_text.get(start_idx, f'{start_idx}+20c'))}c"
        code_text.tag_add("number", start_idx, end_idx)
        start_idx = end_idx

    code_text.tag_configure("number", foreground="#b5cea8")  # Number color

# ฟังก์ชันสำหรับแสดงเลขบรรทัด
def update_line_numbers(event=None):
    line_numbers.delete(1.0, tk.END)
    line_count = int(code_text.index('end-1c').split('.')[0])
    for i in range(1, line_count + 1):
        line_numbers.insert(tk.END, f"{i}\n")

# ฟังก์ชันสำหรับค้นหา
def find_text():
    search_query = tkinter.simpledialog.askstring("Find", "Enter text to search:")
    if search_query:
        start_idx = '1.0'
        while True:
            start_idx = code_text.search(search_query, start_idx, stopindex=tk.END)
            if not start_idx:
                break
            end_idx = f"{start_idx}+{len(search_query)}c"
            code_text.tag_add("highlight", start_idx, end_idx)
            start_idx = end_idx
        code_text.tag_configure("highlight", background="yellow", foreground="black")

# ฟังก์ชันสำหรับการย่อหน้าอัตโนมัติ
def auto_indent(event):
    line = code_text.get("insert linestart", "insert lineend")
    indent = "    "  # 4 spaces
    if line.strip() == "":
        code_text.insert("insert", indent)
    return 'break'

# ฟังก์ชันเปลี่ยนธีม
def toggle_theme():
    current_bg = root.cget("bg")
    if current_bg == "#2e2e2e":  # Dark Mode
        root.config(bg="#f5f5f5")
        code_text.config(bg="#ffffff", fg="#000000")
        line_numbers.config(bg="#f5f5f5", fg="#000000")
    else:  # Light Mode
        root.config(bg="#2e2e2e")
        code_text.config(bg="#1e1e1e", fg="#d4d4d4")
        line_numbers.config(bg="#2e2e2e", fg="white")

# ฟังก์ชันสำหรับบันทึก error log
def log_error(message):
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, "error_log.txt")
    try:
        with open(log_file, 'a', encoding='utf-8') as file:
            file.write(f"{message}\n")
    except Exception as e:
        messagebox.showerror("Error", f"Error logging message: {e}")

# ฟังก์ชันการอัปเดต
def check_for_updates():
    try:
        # Send a request to the GitHub API to get the latest release info
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes

        latest_release = response.json()
        latest_version = latest_release['tag_name']  # Get the latest version (e.g., v1.0.1)
        release_url = latest_release['html_url']  # URL to the release page

        current_version = "v1.0.0"  # Define your current version (should be dynamically set)

        # Compare versions
        if latest_version != current_version:
            messagebox.showinfo("Update Available", 
                                f"A new version ({latest_version}) is available! Visit {release_url} to download it.")
        else:
            messagebox.showinfo("Update", "Xeno Editor is up to date!\nVersion 1.0.0 Beta Test")

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to check for updates: {e}")

    # Call check_for_updates again after 1 hour (3600000 ms)
    root.after(3600000, check_for_updates)

# สร้างหน้าต่างหลัก
root = tk.Tk()
root.title("Xeno Editor")

# ตั้งค่าพื้นหลังของหน้าต่างเป็นสีมืด
root.config(bg="#2e2e2e")

# สร้าง menu bar
menu_bar = tk.Menu(root)

# สร้างเมนู "File"
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# สร้างเมนู "Help"
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About", command=show_message)
help_menu.add_command(label="Check for Updates", command=check_for_updates)

# เพิ่มเมนู "File" และ "Help" ลงใน menu bar
menu_bar.add_cascade(label="File", menu=file_menu)
menu_bar.add_cascade(label="Help", menu=help_menu)

# เชื่อมโยง menu bar เข้ากับหน้าต่างหลัก
root.config(menu=menu_bar)

# สร้าง ttk.Notebook สำหรับสร้างแท็บ
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# สร้าง Tab สำหรับการเขียนโค้ด
code_tab = tk.Frame(notebook, bg="#2e2e2e")
notebook.add(code_tab, text="Code Editor")

# สร้าง Tab สำหรับการแสดงผล
output_tab = tk.Frame(notebook, bg="#2e2e2e")
notebook.add(output_tab, text="Output")

# สร้าง Frame สำหรับการจัดเรียง widget ขนาน
frame = tk.Frame(code_tab, bg="#2e2e2e")
frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# เพิ่ม Frame สำหรับแสดงเลขบรรทัด
line_numbers_frame = tk.Frame(frame, bg="#2e2e2e")
line_numbers_frame.pack(side=tk.LEFT, fill=tk.Y)

line_numbers = tk.Text(line_numbers_frame, height=10, width=5, bg="#2e2e2e", fg="white", bd=0, font=("Segoe UI", 10), wrap=tk.NONE)
line_numbers.pack(side=tk.LEFT, fill=tk.Y)

# เพิ่ม Text widget สำหรับการพิมพ์ข้อความใน Frame
code_text = tk.Text(frame, wrap=tk.WORD, height=10, width=50, bg="#1e1e1e", fg="#d4d4d4", insertbackground="white", font=("Segoe UI", 10))
code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# เพิ่ม Scrollbar สำหรับ Text widget
scrollbar = tk.Scrollbar(frame, command=code_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# เชื่อมโยง Scrollbar กับ Text widget
code_text.config(yscrollcommand=scrollbar.set)

# สร้างปุ่ม 'Run'
run_button = tk.Button(root, text="Run", command=run_code, bg="#4CAF50", fg="white", relief="flat", font=("Segoe UI", 12))
run_button.pack(pady=5)

# ปรับปรุงเลขบรรทัดทุกครั้งที่มีการพิมพ์
code_text.bind("<KeyRelease>", update_line_numbers)

# เริ่มต้นการอัปเดต
check_for_updates()

# สร้างหน้าต่างหลักให้แสดง
root.mainloop()

# Bind the 'Ctrl+F' key combination to the find_text function
root.bind("<Control-f>", lambda event: find_text())

# ฟังก์ชัน Auto-indent
code_text.bind("<Return>", auto_indent)
