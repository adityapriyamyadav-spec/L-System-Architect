#  L-System Architect

A real-time fractal generator built with **Python**, **Tkinter**, and **Turtle**.

This tool renders **Lindenmayer Systems** (math-based fractals) on a custom **Infinite Canvas**. It features a unique "Smart Drag" system that solves standard library limitations, allowing smooth panning, zooming, and interaction without glitches.

**Zero external dependencies required.** (Runs on standard Python).

![Project Screenshot](https://via.placeholder.com/800x400?text=Run+App+To+Take+Screenshot)

##  Key Features

* **♾️ Infinite Canvas:** Pan and zoom freely across a massive 1,000,000px virtual space.
* **🖱️ Smart-Drag Navigation:** Custom vector logic distinguishes between clicking (to set start points) and dragging (to pan the view).
* **🎲 Chaos Mode:** Adds random noise to angles for organic, hand-drawn fractal effects.
* **🎨 Themes:** Pre-loaded with professional color palettes (Google Brand, Cyberpunk, Sunset).
* **📋 DNA Sharing:** Copy/paste fractal "Axioms" and "Rules" to share with others.

##  How to Run

1.  **Clone the repo:**
    ```bash
    git clone [https://github.com/yourusername/l-system-architect.git](https://github.com/yourusername/l-system-architect.git)
    ```
2.  **Enter the folder:**
    ```bash
    cd l-system-architect
    ```
3.  **Run the app:**
    ```bash
    python main.py
    ```

*(Optional: Install `pip install Pillow` if you want to save high-res PNGs. Otherwise, it saves as Vector EPS).*

## 🎮 Controls

| Action | Control |
| :--- | :--- |
| **Pan View** | Left Click + Drag |
| **Set Start Point** | Left Click (Quick Tap) |
| **Zoom** | Scroll Wheel |
| **Reset View** | Click "📍 Reset View" Button |
| **Alternate Pan** | Spacebar + Drag |

##  Supported Fractals
* **Koch Snowflake**
* **Dragon Curve**
* **Sierpinski Triangle**
* **Fractal Plant**
* **Gosper Curve** (Hexagonal)

##  Tech Stack
* **Language:** Python 3.x
* **GUI:** Tkinter
* **Rendering:** Turtle Graphics
* **Logic:** String Rewriting Systems (L-Systems)
