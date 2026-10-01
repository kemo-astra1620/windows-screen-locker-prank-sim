import os
import random
import subprocess
import sys
import tkinter as tk
import ctypes
from ctypes import wintypes

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
            box_x1 + 200, bar_y, box_x1 + 200, bar_y + 16, fill="#00FF33", outline=""
        )
        self.progress_text_id = self.canvas.create_text(
            (box_x1 + 200 + box_x2) / 2, bar_y + 8, text="%0", fill="black", font=("Courier", 9, "bold")
        )

        self.footer_text_id = self.canvas.create_text(
            self.width / 2,
            self.height - 25,
            text="GÜVENLİK DUVARI: %100",
            fill="white",
            font=("Courier", 15, "bold"),
        )

        self.scanner_line_id = self.canvas.create_line(
            0, 0, self.width, 0, fill="#002211", width=2
        )

    def init_subtle_matrix(self):
        self.matrix_drops = []
        for _ in range(25):
            self.matrix_drops.append({
                "x": random.randint(50, self.width - 50),
                "y": random.randint(-self.height, 0),
                "speed": random.randint(3, 8),
                "text": random.choice("0101010101ABCDEF_ROOT")
            })

    def animate_hud_scanner(self):
        if not self.running or self.wipe_mode or self.goodbye_mode:
            return

        self.scan_line_y += self.scan_direction * 12
        if self.scan_line_y > self.height or self.scan_line_y < 0:
            self.scan_direction *= -1

        self.canvas.coords(self.scanner_line_id, 0, self.scan_line_y, self.width, self.scan_line_y)

        for drop in self.matrix_drops:
            drop["y"] += drop["speed"]
            if drop["y"] > self.height:
                drop["y"] = random.randint(-200, -20)

        self.root.after(35, self.animate_hud_scanner)

    def update_breach_timer(self):
        if not self.running or self.wipe_mode or self.goodbye_mode:
            return
        
        mins = self.timer_seconds // 60
        secs = self.timer_seconds % 60
        time_str = f"ELAPSED: {mins:02d}:{secs:02d}"
        self.canvas.itemconfig(self.timer_text_id, text=time_str)
        
        self.timer_seconds += 1
        self.root.after(1000, self.update_breach_timer)

    def update_progress_bar(self):
        if not self.running or self.wipe_mode or self.goodbye_mode:
            return

        if self.progress_percent < 100:
            step = random.randint(1, 3)
            self.progress_percent += step
            if self.progress_percent > 100:
                self.progress_percent = 100

            box_width = int(self.width * 0.6)
            box_x1 = (self.width - box_width) / 2
            box_x2 = box_x1 + box_width
            bar_start_x = box_x1 + 200
            
            current_fill_x = bar_start_x + (box_x2 - bar_start_x) * (self.progress_percent / 100)
            
            bar_y = self.canvas.coords(self.bar_bg)[1]
            self.canvas.coords(self.progress_bar_fill, bar_start_x, bar_y, current_fill_x, bar_y + 16)
            self.canvas.itemconfig(self.progress_text_id, text=f"%{self.progress_percent}")

            firewall_percent = 100 - self.progress_percent
            self.canvas.itemconfig(
                self.footer_text_id,
                text=f"GÜVENLİK DUVARI: %{firewall_percent}"
            )

            if self.progress_percent == 100:
                self.trigger_system_wipe()
                return

        self.root.after(700, self.update_progress_bar)

    def trigger_system_wipe(self):
        self.wipe_mode = True
        
        self.canvas.configure(bg="#1a0000")
        self.canvas.delete("all")

        self.canvas.create_text(
            self.width / 2, 35,
            text="[ ! ] KRİTİK HATA: TÜM VERİLER SİLİNİYOR [ ! ]",
            fill="red", font=("Courier", 19, "bold")
        )

        self.wipe_lines = []
        start_y = 75
        end_y = self.height - 40
        step_y = 26

        for y_pos in range(start_y, end_y, step_y):
            txt_id = self.canvas.create_text(
                50, y_pos, text="", fill="#FF3333", font=("Courier", 11, "bold"), anchor="nw"
            )
            self.wipe_lines.append(txt_id)

        self.fast_wipe_animation()
        self.root.after(10000, self.show_goodbye_screen)

    def fast_wipe_animation(self):
        if not self.running or self.goodbye_mode:
            return

        wipe_pool = [
            "rm -rf / --no-preserve-root [OK]",
            "shred -u -z -n 5 /dev/sda [DELETED]",
            "Overwriting Master Boot Record (MBR) sectors...",
            "Purging cryptographic keys and keychains...",
            "Unlinking user profiles and registry hives...",
            "Zeroing out physical memory blocks (RAM dump)...",
            "Terminating kernel threads and active daemons...",
            "FATAL: Partition table corrupted beyond recovery.",
            "System self-destruct sequence fully executed."
        ]

        for i in range(len(self.wipe_lines) - 1):
            current_text = self.canvas.itemcget(self.wipe_lines[i+1], "text")
            self.canvas.itemconfig(self.wipe_lines[i], text=current_text)

        new_random_wipe = random.choice(wipe_pool) + " -> " + hex(random.randint(0x10000, 0xFFFFF))
        self.canvas.itemconfig(self.wipe_lines[-1], text=new_random_wipe)

        self.root.after(60, self.fast_wipe_animation)

    def show_goodbye_screen(self):
        if not self.running:
            return
        
        self.goodbye_mode = True
        self.canvas.configure(bg="black")
        self.canvas.delete("all")

        self.canvas.create_text(
            self.width / 2, self.height / 2,
            text="GOODBYE",
            fill="#FF0033",
            font=("Courier", 64, "bold"),
            anchor="center"
        )

        self.root.after(3000, self.exit_simulation)

    def exit_simulation(self):
        self.running = False
        uninstall_keyboard_hook()
        self.root.destroy()
        sys.exit(0)

    def typewriter_terminal(self):
        if not self.running or self.wipe_mode or self.goodbye_mode:
            return

        target_text = self.logs_pool[self.current_log_index]

        if self.char_index <= len(target_text):
            current_displayed = target_text[:self.char_index] + "_"
            self.canvas.itemconfig(self.current_line_id, text=current_displayed)
            self.char_index += 1
            self.root.after(20, self.typewriter_terminal)
        else:
            self.canvas.itemconfig(self.current_line_id, text=target_text)
            self.displayed_lines.append(self.current_line_id)

            bx1, by1, bx2, by2 = self.console_box_coords
            
            if len(self.displayed_lines) > 6:
                old_id = self.displayed_lines.pop(0)
                self.canvas.delete(old_id)

            y_offset = by1 + 6
            for line_id in self.displayed_lines:
                self.canvas.coords(line_id, bx1, y_offset)
                y_offset += 18

            self.current_log_index = (self.current_log_index + 1) % len(self.logs_pool)
            self.char_index = 0

            self.current_line_id = self.canvas.create_text(
                bx1,
                y_offset,
                text="",
                fill="#00FF66",
                font=("Courier", 9),
                anchor="nw"
            )

            self.root.after(800, self.typewriter_terminal)

    def keep_focus(self):
        if self.running:
            self.root.focus_force()
            self.root.after(500, self.keep_focus)

    def bind_events(self):
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.bind("<KeyPress>", self.handle_keypress)

    def handle_keypress(self, event):
        if event.keysym == "Escape":
            self.exit_simulation()
        return "break"


if __name__ == "__main__":
    install_keyboard_hook()

    root = tk.Tk()
    app = SupremeScreenLocker(root)
    
    try:
        root.mainloop()
    finally:
        uninstall_keyboard_hook()
