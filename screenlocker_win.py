import os
import random
import subprocess
import sys
import tkinter as tk
import ctypes
from ctypes import wintypes
import keyboard  # Klavye engelleme kütüphanesi

PIL_AVAILABLE = False
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    pass

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
    ]

VK_TAB = 0x09
VK_ESCAPE = 0x1B
VK_LWIN = 0x5B
VK_RWIN = 0x5C
VK_CONTROL = 0x11
VK_MENU = 0x12

hook_id = None
hook_proc_ref = None

def low_level_keyboard_handler(nCode, wParam, lParam):
    if nCode >= 0 and (wParam == WM_KEYDOWN or wParam == WM_SYSKEYDOWN):
        kb_struct = KBDLLHOOKSTRUCT.from_address(lParam)
        vk = kb_struct.vkCode

        if vk == VK_ESCAPE:
            return user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

        is_alt_pressed = (kb_struct.flags & 0x20) != 0
        if vk in (VK_LWIN, VK_RWIN):
            return 1
        if is_alt_pressed and vk == VK_TAB:
            return 1
        if is_alt_pressed and vk == 0x73:
            return 1
        if vk == VK_ESCAPE and (user32.GetKeyState(VK_CONTROL) & 0x8000):
            return 1

    return user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

def install_keyboard_hook():
    global hook_id, hook_proc_ref
    hook_proc_ref = HOOKPROC(low_level_keyboard_handler)
    module_handle = kernel32.GetModuleHandleW(None)
    hook_id = user32.SetWindowsHookExW(WH_KEYBOARD_LL, hook_proc_ref, module_handle, 0)

def uninstall_keyboard_hook():
    global hook_id
    if hook_id:
        user32.UnhookWindowsHookEx(hook_id)
        hook_id = None

# Keyboard kütüphanesi tuş kilitleri
def block_special_keys():
    keyboard.block_key('left windows')
    keyboard.block_key('right windows')
    keyboard.block_key('alt')
    keyboard.block_key('ctrl')
    keyboard.block_key('tab')

def unblock_special_keys():
    keyboard.unblock_key('left windows')
    keyboard.unblock_key('right windows')
    keyboard.unblock_key('alt')
    keyboard.unblock_key('ctrl')
    keyboard.unblock_key('tab')


class SupremeScreenLocker:

    def __init__(self, root):
        self.root = root
        
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        self.root.overrideredirect(True)
        self.root.geometry(f"{self.width}x{self.height}+0+0")
        self.root.configure(bg="black")
        self.root.config(cursor="none")

        self.root.attributes("-topmost", True)
        self.root.focus_force()

        self.image_filename = "hacker.png"
        self.tk_image = None
        if PIL_AVAILABLE:
            self.load_image()

        self.create_widgets()
        self.bind_events()

        # Kilitleri devreye al
        install_keyboard_hook()
        block_special_keys()

        self.running = True
        self.scan_line_y = 0
        self.scan_direction = 1
        self.timer_seconds = 0
        self.progress_percent = 0
        self.wipe_mode = False
        self.goodbye_mode = False

        self.current_log_index = 0
        self.char_index = 0
        self.logs_pool = [
            "[+] Target IP: 192.168.1.105 -> Port 443 [EXPLOITED]",
            "[!] Bypassing Windows Defender heuristic analysis...",
            "[*] Extracting SAM database hashes from memory...",
            "[#] Escalating privileges: LocalSystem -> Administrator...",
            "[+] Meterpreter session 1 opened (10.0.2.15:4444)",
            "[-] Wiping system event logs and audit trails...",
            "[*] Injecting payload into explorer.exe thread...",
            "[+] Rootkit successfully installed on virtual partition.",
            "[!] Warning: Remote access channel secured and encrypted."
        ]
        self.displayed_lines = []

        self.init_subtle_matrix()
        self.animate_hud_scanner()
        self.update_breach_timer()
        self.update_progress_bar()
        self.typewriter_terminal()
        self.keep_focus()

    def load_image(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, self.image_filename)

        if not os.path.exists(image_path):
            return

        try:
            self.pil_image = Image.open(image_path)
            aspect_ratio = self.pil_image.height / self.pil_image.width
            target_width = int(min(self.width * 0.22, 340))
            target_height = int(target_width * aspect_ratio)

            if self.pil_image.width > target_width:
                self.pil_image = self.pil_image.resize(
                    (target_width, target_height), Image.Resampling.LANCZOS
                )

            self.tk_image = ImageTk.PhotoImage(self.pil_image)
        except Exception:
            self.tk_image = None

    def create_widgets(self):
        self.canvas = tk.Canvas(
            self.root,
            bg="black",
            highlightthickness=0,
            width=self.width,
            height=self.height,
        )
        self.canvas.pack(fill="both", expand=True)

        self.status_text_id = self.canvas.create_text(
            30, 25, text="STATUS: SYSTEM HIJACKED", fill="#FF0033", font=("Courier", 13, "bold"), anchor="nw"
        )
        self.canvas.create_text(
            30, 45, text="PROTOCOL: FSOCIETY_OVERRIDE_V4", fill="#00FF66", font=("Courier", 13), anchor="nw"
        )
        
        self.timer_text_id = self.canvas.create_text(
            self.width - 30, 25, text="ELAPSED: 00:00", fill="#00FF66", font=("Courier", 12, "bold"), anchor="ne"
        )

        image_offset = 0
        if self.tk_image:
            center_x = self.width / 2
            top_y = self.height * 0.025
            self.canvas.create_image(
                center_x, top_y, image=self.tk_image, anchor="n"
            )
            image_offset = self.tk_image.height()

        text_y_start = self.height * 0.025 + image_offset + 10

        self.title_text_id = self.canvas.create_text(
            self.width / 2,
            text_y_start,
            text="[ fsociety - SİSTEM BAĞLANTISI KURULDU ]",
            fill="#FF0033",
            font=("Courier", 20, "bold"),
        )

        quote = (
            "“Bir adama silah verin bir banka soyabilir, \n"
            "bir adama internet verin bütün dünyayı soyabilir.”"
        )
        self.quote_text_id = self.canvas.create_text(
            self.width / 2,
            text_y_start + 40,
            text=quote,
            fill="#00FF66",
            font=("Courier", 12, "italic"),
            justify="center",
        )

        box_width = int(self.width * 0.6)
        box_height = 180
        box_x1 = (self.width - box_width) / 2
        box_y1 = text_y_start + 75
        box_x2 = box_x1 + box_width
        box_y2 = box_y1 + box_height

        self.box_rect_id = self.canvas.create_rectangle(
            box_x1, box_y1, box_x2, box_y2, outline="#00FF33", fill="#020202", width=2
        )
        self.box_title_rect = self.canvas.create_rectangle(
            box_x1, box_y1, box_x2, box_y1 + 22, fill="#00FF33", outline="#00FF33"
        )
        self.box_title_text = self.canvas.create_text(
            box_x1 + 10,
            box_y1 + 11,
            text="root@kemo:~# ./kernel_exploit --exec",
            fill="black",
            font=("Courier", 9, "bold"),
            anchor="w",
        )

        self.console_box_coords = (box_x1 + 15, box_y1 + 32, box_x2 - 15, box_y2 - 10)
        
        self.current_line_id = self.canvas.create_text(
            box_x1 + 15,
            box_y1 + 38,
            text="",
            fill="#00FF66",
            font=("Courier", 9),
            anchor="nw"
        )

        bar_y = box_y2 + 20
        self.progress_label_id = self.canvas.create_text(
            box_x1, bar_y, text="VERİ SIZINTI İLERLEMESİ:", fill="#00FF66", font=("Courier", 9, "bold"), anchor="nw"
        )
        
        self.bar_bg = self.canvas.create_rectangle(
            box_x1 + 200, bar_y, box_x2, bar_y + 16, outline="#00FF33", fill="#111111"
        )
        
        self.progress_bar_fill = self.canvas.create_rectangle(
            box_x1 + 200, bar_y, box_x1 + 200, bar_y + 16, outline="", fill="#00FF33"
        )

    def bind_events(self):
        self.root.bind("<Escape>", self.exit_program)

    def exit_program(self, event=None):
        self.running = False
        uninstall_keyboard_hook()
        unblock_special_keys()
        self.root.destroy()
        sys.exit(0)

    def init_subtle_matrix(self):
        pass

    def animate_hud_scanner(self):
        if not self.running: return
        self.root.after(30, self.animate_hud_scanner)

    def update_breach_timer(self):
        if not self.running: return
        self.timer_seconds += 1
        mins = self.timer_seconds // 60
        secs = self.timer_seconds % 60
        self.canvas.itemconfig(self.timer_text_id, text=f"ELAPSED: {mins:02d}:{secs:02d}")
        self.root.after(1000, self.update_breach_timer)

    def update_progress_bar(self):
        if not self.running: return
        if self.progress_percent < 100:
            self.progress_percent += 1
            box_width = int(self.width * 0.6)
            box_x1 = (self.width - box_width) / 2
            box_x2 = box_x1 + box_width
            start_x = box_x1 + 200
            max_w = box_x2 - start_x
            current_w = start_x + (max_w * (self.progress_percent / 100))
            bg_coords = self.canvas.coords(self.bar_bg)
            if bg_coords:
                self.canvas.coords(self.progress_bar_fill, start_x, bg_coords[1], current_w, bg_coords[3])
        self.root.after(200, self.update_progress_bar)
    def typewriter_terminal(self):
        if not self.running: return
        if self.current_log_index < len(self.logs_pool):
            current_str = self.logs_pool[self.current_log_index]
            if self.char_index < len(current_str):
                self.char_index += 1
                display_text = "\n".join(self.displayed_lines) + "\n" + current_str[:self.char_index]
                self.canvas.itemconfig(self.current_line_id, text=display_text)
                self.root.after(30, self.typewriter_terminal)
            else:
                self.displayed_lines.append(current_str)
                self.current_log_index += 1
                self.char_index = 0
                self.root.after(400, self.typewriter_terminal)
    def keep_focus(self):
        if not self.running: 
            return
        self.root.focus_force()
        self.root.attributes("-topmost", True)
        self.root.after(10, self.keep_focus)
if __name__ == "__main__":
    root = tk.Tk()
    app = SupremeScreenLocker(root)
    root.mainloop()
