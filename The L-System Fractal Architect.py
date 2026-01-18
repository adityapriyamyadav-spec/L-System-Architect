import tkinter as tk
from tkinter import messagebox, colorchooser, filedialog
from turtle import RawTurtle, TurtleScreen
import random
import colorsys
import math
import os

# Check if Pillow is installed for PNG support
try:
    from PIL import Image, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# --- 1. CONFIGURATION ---

GOOGLE_BLUE = "#4285F4"
GOOGLE_RED = "#EA4335"
GOOGLE_YELLOW = "#FBBC05"
GOOGLE_GREEN = "#34A853"
DARK_BG = "#202124"
TEXT_WHITE = "#E8EAED"

DEFAULT_START_X = 0
DEFAULT_START_Y = -300
start_x = DEFAULT_START_X
start_y = DEFAULT_START_Y

FRACTAL_LIBRARY = {
    "Select a Preset...": {"axiom": "", "rules": "", "angle": 0},
    "Koch Snowflake": {"axiom": "F--F--F", "rules": "F:F+F--F+F", "angle": 60},
    "Arrowheads": {"axiom": "A", "rules": "A:B-A-B, B:A+B+A", "angle": 60}, 
    "Fractal Plant": {"axiom": "X", "rules": "X:F-[[X]+X]+F[+FX]-X, F:FF", "angle": 25},
    "Dragon Curve": {"axiom": "FX", "rules": "X:X+YF+, Y:-FX-Y", "angle": 90},
    "Hex Badge": {"axiom": "A", "rules": "A:A-B--B+A++AA+B-, B:+A-BB--B-A++A+B", "angle": 60},
    "Sierpinski": {"axiom": "F-G-G", "rules": "F:F-G+F+G-F, G:GG", "angle": 120},
}

COLOR_PALETTES = {
    "Rainbow": [], 
    "Google Brand": [GOOGLE_BLUE, GOOGLE_RED, GOOGLE_YELLOW, GOOGLE_GREEN],
    "Forest": ["#2D5A27", "#1E4D2B", "#8FBC8F", "#228B22", "#006400", "#556B2F"],
    "Ocean": ["#000080", "#0000CD", "#4169E1", "#00BFFF", "#E0FFFF", "#4682B4"],
    "Neon": ["#FF00FF", "#00FFFF", "#FFFF00", "#FF1493", "#00FF00", "#FF4500"],
    "Cyberpunk": ["#FF007F", "#00F3FF", "#711C91", "#05FFA1", "#FFFFFF"],
    "Sunset": ["#FF4500", "#FF8C00", "#FFD700", "#C71585", "#8B0000"],
}

# --- 2. HELPERS ---

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text: return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, background="#ffffe0", relief=tk.SOLID, borderwidth=1, font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

def log_to_console(message):
    print(f"[Log] {message}")

# --- 3. LOGIC ---

def expand_l_system(axiom, rules_text, iterations):
    rules = {}
    for rule in rules_text.split(","):
        if ":" in rule:
            key, val = rule.split(":")
            rules[key.strip()] = val.strip()

    current_string = axiom
    for i in range(iterations):
        current_string = "".join([rules.get(char, char) for char in current_string])
    return current_string

def draw_l_system(t, instructions, angle, distance, is_chaotic, palette_name, taper):
    stack = []
    variation = 0.2 if is_chaotic else 0.0
    total_steps = len(instructions)
    palette = COLOR_PALETTES.get(palette_name, [])
    color_index = 0
    
    for i, cmd in enumerate(instructions):
        if not palette: 
            hue = i / total_steps
            t.pencolor(colorsys.hsv_to_rgb(hue, 1.0, 1.0))
        else:
            t.pencolor(palette[color_index % len(palette)])
            color_index += 1

        if cmd in ['F', 'G', 'A', 'B']:
            step = distance * (1 + random.uniform(-variation, variation))
            t.forward(step)
        elif cmd == '+':
            t.right(angle * (1 + random.uniform(-variation, variation)))
        elif cmd == '-':
            t.left(angle * (1 + random.uniform(-variation, variation)))
        elif cmd == '[':
            stack.append((t.position(), t.heading(), t.pensize()))
            if taper: t.pensize(max(1, t.pensize() * 0.75))
        elif cmd == ']':
            pos, head, size = stack.pop()
            t.penup()
            t.setposition(pos)
            t.setheading(head)
            t.pensize(size)
            t.pendown()

# --- 4. PANNING & ZOOM ENGINE ---

# Variables to distinguish between a "Click" (Set Dot) and a "Drag" (Pan)
mouse_start_x = 0
mouse_start_y = 0
is_dragging = False

def enforce_scroll_region():
    """Forces the canvas to be massive so panning never gets stuck."""
    canvas.config(scrollregion=(-50000, -50000, 50000, 50000))

def on_mouse_down(event):
    """Start tracking the mouse."""
    global mouse_start_x, mouse_start_y, is_dragging
    mouse_start_x = event.x
    mouse_start_y = event.y
    is_dragging = False
    
    # "Mark" the anchor point for scrolling
    canvas.scan_mark(event.x, event.y)

def on_mouse_move(event):
    """Handle dragging motion."""
    global is_dragging
    
    # Calculate distance moved
    dist = math.hypot(event.x - mouse_start_x, event.y - mouse_start_y)
    
    # Only treat as a drag if moved more than 3 pixels
    if dist > 3:
        is_dragging = True
        # Move the canvas content
        canvas.scan_dragto(event.x, event.y, gain=1)

def on_mouse_up(event):
    """Handle release - did we click or drag?"""
    if not is_dragging:
        # It was a simple CLICK -> Set the Red Dot
        # Get logic coordinates (accounting for zoom/pan)
        canv_x = canvas.canvasx(event.x)
        canv_y = canvas.canvasy(event.y)
        set_start_pos(canv_x, -canv_y)

def set_start_pos(x, y):
    global start_x, start_y
    start_x, start_y = x, y
    
    # Draw the dot
    screen.tracer(1)
    t.penup()
    t.goto(start_x, start_y)
    t.dot(10, GOOGLE_RED) 
    t.pendown()
    screen.tracer(0)
    print(f"Start Point set to: {int(x)}, {int(y)}")

def reset_view():
    """Centers the camera back to (0,0)."""
    canvas.xview_moveto(0.5)
    canvas.yview_moveto(0.5)

def wheel_zoom(event):
    scale_factor = 1.0
    # Mac/Windows scroll handling
    if event.num == 5 or event.delta < 0: scale_factor = 0.9 
    elif event.num == 4 or event.delta > 0: scale_factor = 1.1 
    
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    canvas.scale("all", x, y, scale_factor, scale_factor)
    
    # Re-enforce scroll region after zoom to prevent getting stuck
    enforce_scroll_region()

def mac_pinch(event):
    try:
        scale = 1.0 + event.delta 
        if scale > 1.0: scale = 1.05 
        if scale < 1.0: scale = 0.95 
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        canvas.scale("all", x, y, scale, scale)
        enforce_scroll_region()
    except Exception: pass 

def clear_canvas():
    global start_x, start_y
    t.clear()
    t.penup()
    t.home()
    t.hideturtle()
    start_x = DEFAULT_START_X
    start_y = DEFAULT_START_Y
    
    canvas.delete("all") 
    reset_view() # Snap back to center
    enforce_scroll_region() # CRITICAL: Re-apply infinite scroll
    
    t.hideturtle() 
    screen.update()

def copy_config():
    config_text = f"Axiom: {entry_axiom.get()} | Rules: {entry_rules.get()}"
    root.clipboard_clear()
    root.clipboard_append(config_text)
    messagebox.showinfo("Copied", "Fractal DNA copied!")

def run_fractal():
    try:
        axiom = entry_axiom.get()
        rules = entry_rules.get()
        angle = float(entry_angle.get())
        iters = int(entry_iter.get())
        base_width = scale_width.get()
        raw_distance = scale_dist.get()
        anim_speed = scale_speed.get()

        if iters > 3: distance = raw_distance / (1.5 ** (iters - 3))
        else: distance = raw_distance

        is_chaotic = bool(chaos_var.get())
        is_animated = bool(anim_var.get())
        taper_mode = bool(taper_var.get())
        selected_palette = palette_var.get()
        
        instructions = expand_l_system(axiom, rules, iters)
        
        t.clear()
        t.penup()
        t.goto(start_x, start_y) 
        t.setheading(90)
        t.pensize(base_width)
        t.pendown()
        
        if is_animated:
            t.speed(0)
            if anim_speed == 10: screen.tracer(50, 0)
            elif anim_speed > 5: screen.tracer(anim_speed * 2, 0)
            else: screen.tracer(1, (6 - anim_speed) * 10)
        else:
            screen.tracer(0, 0)
            t.speed(0)

        draw_l_system(t, instructions, angle, distance, is_chaotic, selected_palette, taper_mode)
        screen.update()
        
        # CRITICAL: Ensure we can still scroll after drawing
        enforce_scroll_region()
        
    except Exception as e:
        log_to_console(f"Error: {e}")

def randomize_inputs():
    random_preset = random.choice(list(FRACTAL_LIBRARY.keys())[1:])
    load_preset(random_preset)
    current_angle = float(entry_angle.get())
    entry_angle.delete(0, tk.END)
    entry_angle.insert(0, str(current_angle + random.randint(-15, 15)))
    safe_iter = random.randint(3, 4)
    entry_iter.delete(0, tk.END)
    entry_iter.insert(0, str(safe_iter))
    scale_dist.set(random.randint(8, 15))
    scale_width.set(random.randint(1, 3))
    palette_var.set(random.choice(list(COLOR_PALETTES.keys())))
    run_fractal()

def load_preset(selection):
    data = FRACTAL_LIBRARY.get(selection)
    if data and selection != "Select a Preset...":
        entry_axiom.delete(0, tk.END)
        entry_axiom.insert(0, data["axiom"])
        entry_rules.delete(0, tk.END)
        entry_rules.insert(0, data["rules"])
        entry_angle.delete(0, tk.END)
        entry_angle.insert(0, str(data["angle"]))

def choose_background():
    color = colorchooser.askcolor(title="Choose Background")[1]
    if color:
        canvas.config(bg=color)
        screen.bgcolor(color)

def save_image():
    # 1. Ask where to save
    filename = filedialog.asksaveasfilename(defaultextension=".png", 
                                            filetypes=[("PNG Image", "*.png"), ("Vector EPS", "*.eps")])
    if not filename: return

    # 2. Tkinter can ONLY save as EPS first (we use this as a temp file)
    temp_eps = filename.replace(".png", ".eps")
    canvas.postscript(file=temp_eps, colormode='color')

    # 3. If filename is EPS, we are done
    if filename.endswith(".eps"):
        messagebox.showinfo("Saved", f"Saved Vector EPS: {filename}")
        return

    # 4. Try to convert EPS -> PNG
    if HAS_PIL:
        try:
            with Image.open(temp_eps) as img:
                # Ghostscript is sometimes needed by PIL to read EPS
                img.load(scale=4) # 4x High Resolution scale
                img.save(filename, 'png')
            
            # Cleanup: Delete the temp EPS file so user only sees PNG
            if os.path.exists(temp_eps):
                os.remove(temp_eps)
                
            messagebox.showinfo("Success", f"High-Res PNG Saved!\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Conversion Error", f"Saved as EPS instead.\n\nError: {e}\n(You might need to install Ghostscript for EPS support)")
    else:
        messagebox.showwarning("Pillow Missing", "Python 'Pillow' library not found.\nSaved as .eps (Vector) instead.\n\nRun: pip install Pillow")
def show_about():
    messagebox.showinfo("About", "L-System Architect\n\nControls:\n• LEFT CLICK + DRAG: Pan Canvas\n• LEFT CLICK (QUICK): Set Red Dot\n• SPACE + DRAG: Alternate Pan\n• SCROLL: Zoom")

# --- 5. UI SETUP ---

root = tk.Tk()
# MODIFIED TITLE HERE
root.title("L-System Architect")
root.geometry("1200x800") 
root.configure(bg=DARK_BG)

menubar = tk.Menu(root)
help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(label="About Project", command=show_about)
menubar.add_cascade(label="Help", menu=help_menu)
root.config(menu=menubar)

label_font = ("Helvetica", 8, "bold")
entry_bg = "#303134"
entry_fg = "white"

controls = tk.Frame(root, padx=2, pady=5, bg=DARK_BG, relief=tk.FLAT)
controls.pack(side=tk.LEFT, fill=tk.Y)

def create_label(text):
    tk.Label(controls, text=text, font=label_font, bg=DARK_BG, fg=TEXT_WHITE).pack(anchor="w", pady=(1,0))

def create_entry(val):
    e = tk.Entry(controls, width=12, bg=entry_bg, fg=entry_fg, insertbackground="white", relief=tk.FLAT)
    e.insert(0, val)
    e.pack(pady=0, ipady=1) 
    return e

create_label("Axiom:")
entry_axiom = create_entry("F")
ToolTip(entry_axiom, "Start string")

create_label("Rules:")
entry_rules = create_entry("F:F[+F]F[-F]F")

create_label("Angle:")
entry_angle = create_entry("25")
create_label("Iter:") 
entry_iter = create_entry("4")

create_label("Step:")
scale_dist = tk.Scale(controls, from_=5, to=50, orient=tk.HORIZONTAL, bg=DARK_BG, fg=TEXT_WHITE, highlightthickness=0)
scale_dist.set(15)
scale_dist.pack(fill=tk.X)

create_label("Speed:")
scale_speed = tk.Scale(controls, from_=1, to=10, orient=tk.HORIZONTAL, bg=DARK_BG, fg=TEXT_WHITE, highlightthickness=0)
scale_speed.set(10)
scale_speed.pack(fill=tk.X)

create_label("Width:")
scale_width = tk.Scale(controls, from_=1, to=10, orient=tk.HORIZONTAL, bg=DARK_BG, fg=TEXT_WHITE, highlightthickness=0)
scale_width.set(2)
scale_width.pack(fill=tk.X)

frame_toggles = tk.Frame(controls, bg=DARK_BG)
frame_toggles.pack(fill=tk.X, pady=2)
taper_var = tk.IntVar(value=1)
tk.Checkbutton(frame_toggles, text="Taper", variable=taper_var, bg=DARK_BG, fg=TEXT_WHITE, selectcolor=DARK_BG, activebackground=DARK_BG, font=("Helvetica", 8)).pack(side=tk.LEFT)
chaos_var = tk.IntVar()
tk.Checkbutton(frame_toggles, text="Chaos", variable=chaos_var, bg=DARK_BG, fg=TEXT_WHITE, selectcolor=DARK_BG, activebackground=DARK_BG, font=("Helvetica", 8)).pack(side=tk.LEFT)
anim_var = tk.IntVar()
tk.Checkbutton(frame_toggles, text="Anim", variable=anim_var, bg=DARK_BG, fg=TEXT_WHITE, selectcolor=DARK_BG, activebackground=DARK_BG, font=("Helvetica", 8)).pack(side=tk.LEFT)

create_label("Palette:")
palette_var = tk.StringVar(value="Rainbow")
tk.OptionMenu(controls, palette_var, *COLOR_PALETTES.keys()).pack(fill=tk.X, pady=1)

create_label("Preset:")
preset_var = tk.StringVar(value="Select...")
tk.OptionMenu(controls, preset_var, *FRACTAL_LIBRARY.keys(), command=load_preset).pack(fill=tk.X, pady=1)

btn_lucky = tk.Button(controls, text="🎲 Lucky", command=randomize_inputs, bg=GOOGLE_YELLOW, fg="black", relief=tk.FLAT, font=("Helvetica", 9))
btn_lucky.pack(fill=tk.X, pady=2)

btn_gen = tk.Button(controls, text="▶ RUN", command=run_fractal, bg=GOOGLE_BLUE, fg="black", relief=tk.FLAT, font=("Helvetica", 10, "bold"))
btn_gen.pack(fill=tk.X, pady=2)

btn_share = tk.Button(controls, text="📋 Copy", command=copy_config, bg="#9C27B0", fg="black", relief=tk.FLAT, font=("Helvetica", 9))
btn_share.pack(fill=tk.X, pady=2)

btn_reset = tk.Button(controls, text="📍 Reset View", command=reset_view, bg="#FF9800", fg="black", relief=tk.FLAT, font=("Helvetica", 9))
btn_reset.pack(fill=tk.X, pady=2)

btn_clear = tk.Button(controls, text="🗑️ Clear", command=clear_canvas, bg=GOOGLE_RED, fg="black", relief=tk.FLAT, font=("Helvetica", 9))
btn_clear.pack(fill=tk.X, pady=2)

btn_save = tk.Button(controls, text="💾 PNG", command=save_image, bg=GOOGLE_GREEN, fg="black", relief=tk.FLAT, font=("Helvetica", 9))
btn_save.pack(fill=tk.X, pady=2)

tk.Button(controls, text="🎨 BG", command=choose_background, bg="#5f6368", fg="black", relief=tk.FLAT, font=("Helvetica", 9)).pack(fill=tk.X, pady=2)

# --- INFINITE CANVAS ---
canvas = tk.Canvas(root, width=800, height=800, bg="white", highlightthickness=0)
canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

# Initialize scroll region
enforce_scroll_region()
# Center camera
canvas.xview_moveto(0.5)
canvas.yview_moveto(0.5)

screen = TurtleScreen(canvas)
t = RawTurtle(screen)
t.hideturtle()
t.speed(0)

# --- SMART BINDINGS (CLICK vs DRAG) ---
canvas.bind("<ButtonPress-1>", on_mouse_down)
canvas.bind("<B1-Motion>", on_mouse_move)
canvas.bind("<ButtonRelease-1>", on_mouse_up)

# Backup: Space + Drag
canvas.bind("<space>", lambda e: canvas.scan_mark(e.x, e.y))
canvas.bind("<B1-Motion>", on_mouse_move) # Re-bind logic handles space context implicitly via behavior

# Zoom
canvas.bind("<MouseWheel>", wheel_zoom)
canvas.bind("<Button-4>", wheel_zoom)   
canvas.bind("<Button-5>", wheel_zoom)   

try:
    canvas.bind("<Magnify>", mac_pinch)
except tk.TclError:
    pass 

root.mainloop()