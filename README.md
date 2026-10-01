### 🛠️ Supreme Screen Locker (Prank & Educational Simulation)

A lightweight, full-screen hacker-themed desktop simulation script written in Python. Utilizing Tkinter for GUI rendering and Windows API low-level hooks (ctypes), this tool simulates a dramatic cybersecurity breach UI equipped with automated typewriter terminal logs, fake exfiltration progress bars, simulated wipe animations, and shortcut suppression.

### ⚠️ DISCLAIMER: This project is strictly intended for educational purposes and benign pranks among consenting parties. It does NOT contain malicious code, encrypt files, modify system registries, or destroy data.

### 📌 Features

---🖥️ Full-Screen Immersive UI: Overrides desktop focus with a borderless, top-most black terminal interface.

---⌨️ Keyboard Navigation Intercept: Demonstrates low-level Windows API hooks (SetWindowsHookExW) to capture and suppress system hotkeys like Alt+Tab, Alt+F4, and the Windows Key.

### ⚡ Animated Cyber Visuals:

---Simulated HUD scanner overlay and subtle matrix rain streams.

---Real-time typewriter output printing simulated penetration testing terminal logs.

---Fake data breach progress indicator and automated system wipe sequence.

---🖼️ Optional Image Branding: Automatically scales and overlays a custom image (hacker.png) if Pillow (PIL) is present.

---🚨 Safe Emergency Exit: Pressing ESC immediately unhooks system hooks and closes the application cleanly without making any system changes.

### ⚙️️ How It Works (Technical Overview)

### 1.Low-Level Keyboard Hooking:
The script registers a low-level keyboard hook using ctypes.windll.user32.SetWindowsHookExW with WH_KEYBOARD_LL. This intercepts keystrokes before they reach standard OS handlers, preventing users from casually minimizing the window via system shortcuts (Alt+Tab, Win Key, etc.).

### 2.Tkinter Canvas Animations:
The GUI utilizes tkinter.Canvas with scheduled callback loops (root.after()) to handle fluid animations (HUD scanner line, matrix streams, and typewriter log simulation).

### 3.Graceful Teardown:
When the ESC key is pressed or the simulation finishes its timer sequence, UnhookWindowsHookEx is explicitly called to release system resources and restore normal keyboard navigation immediately.

### 🚀 Getting Started

--Operating System: Microsoft Windows (10/11 recommended).

--Python Version: Python 3.8 or higher.

### 1.Clone the Repository:
```bash
git clone https://github.com/your-username/supreme-screen-locker.git
cd supreme-screen-locker
```

### 2.(Optional) Install Pillow:
Pillow is optional. If installed, the app will load hacker.png as a banner icon.
```bash
pip install pillow
```

### 3.Run the Script:
```bash
python main.py
```

🛑 How to Exit

To abort or close the simulation at any point:

    Simply press the ESC key on your keyboard.

    The script unhooks all keyboard intercepts and terminates safely.


### ⚖️ Legal & Ethical Compliance

This project complies fully with open-source ethical standards and security software regulations:


1.No Malicious Capability: The script contains zero payload execution, zero ransomware logic, zero system modifications, and zero persistent hooks. All progress bars and terminal outputs are cosmetic strings.

2.Reversible Execution: The application does not write to the disk, modify system startup registers, or disrupt hardware.

3.Consensual & Controlled Use: Users are required to run this software solely on systems they own or have explicit authorization to test on.


### 📄 License

This project is open-source software licensed under the MIT License. Feel free to inspect, modify, and distribute for personal learning or non-malicious fun.
