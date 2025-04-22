from tkinter import Tk, Button, filedialog, Label, Canvas, Scale, HORIZONTAL, Toplevel
from tkinter import ttk
from PIL import Image
from collections import Counter
import math

# Globales metavlites gia ta pixel kai megethos grid
pixels = []
grid_size = 0
green_pixels = []
fixed_pixels = {}  # Dictionary pou apothikeuei ta arxika kai ta διορθωμένα χρώματα

# Leitourgia gia epilogi arxeiou eikonas
def choose_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        extract_colors(file_path, scale.get())

# Leitourgia pou fortonei kai epanalamvanei xromata apo tin eikona
def extract_colors(image_path, resize_factor):
    global pixels, grid_size
    img = Image.open(image_path)
    img = img.resize((resize_factor, resize_factor))
    pixels = list(img.getdata())
    grid_size = resize_factor
    colors = Counter(pixels)
    most_common_colors = colors.most_common(5)

    # Emfanisi ton pio sinithisménon xromáton
    color_labels = "\n".join([f"Color: {color}, Count: {count}" for color, count in most_common_colors])
    label.config(text=color_labels)

    draw_color_grid()

# Sxediazei to grid me ta xromata tis eikonas
def draw_color_grid():
    canvas.delete("all")
    square_size = 500 // grid_size

    for y in range(grid_size):
        for x in range(grid_size):
            color = pixels[y * grid_size + x]
            hex_color = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'
            fill_color = "green" if (x, y) in green_pixels else hex_color
            canvas.create_rectangle(x * square_size, y * square_size, (x + 1) * square_size, (y + 1) * square_size,
                                    fill=fill_color, outline="black")

    # Bind events gia click aristero kai dexi
    canvas.bind("<Button-1>", get_color_on_click)
    canvas.bind("<Button-3>", deselect_colors)

# Epilegei ena xroma me click kai kaloume tin highlight_similar_colors
def get_color_on_click(event):
    square_size = 500 // grid_size
    x = event.x // square_size
    y = event.y // square_size
    selected_color = pixels[y * grid_size + x]
    hex_color = f'#{selected_color[0]:02x}{selected_color[1]:02x}{selected_color[2]:02x}'
    chosen_color_label.config(text=f"Επέλεξες το χρώμα: {hex_color}")
    highlight_similar_colors(selected_color)

# Deksí click: katharizei ta prásina squares (epilogi xromatos)
def deselect_colors(event):
    global green_pixels
    green_pixels.clear()
    draw_color_grid()

# Denei prásino xroma sta grids pou einai konta sto epilegmeno
def highlight_similar_colors(selected_color, tolerance=50):
    global green_pixels
    green_pixels.clear()
    canvas.delete("all")
    square_size = 500 // grid_size

    for y in range(grid_size):
        for x in range(grid_size):
            current_color = pixels[y * grid_size + x]
            if delta_e(selected_color, current_color) < tolerance:
                green_pixels.append((x, y))
            hex_color = f'#{current_color[0]:02x}{current_color[1]:02x}{current_color[2]:02x}'
            fill_color = "green" if (x, y) in green_pixels else hex_color
            canvas.create_rectangle(x * square_size, y * square_size, (x + 1) * square_size, (y + 1) * square_size,
                                    fill=fill_color, outline="black")

# Dioxorthonei ta prásina grids me xromata ton geitonon tous
def fix_green_grids():
    global green_pixels, fixed_pixels
    square_size = 500 // grid_size

    for x, y in green_pixels:
        neighbor_colors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    neighbor_colors.append(pixels[ny * grid_size + nx])
        
        if neighbor_colors:
            original_color = pixels[y * grid_size + x]
            replacement_color = neighbor_colors[0]
            pixels[y * grid_size + x] = replacement_color
            fixed_pixels[(x, y)] = (original_color, replacement_color)

    green_pixels.clear()
    draw_color_grid()

# Apostasi metaksy 2 xromaton me aplo mathimatiko tipo
def delta_e(color1, color2):
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    
    delta_r = r1 - r2
    delta_g = g1 - g2
    delta_b = b1 - b2
    
    return math.sqrt(delta_r ** 2 + delta_g ** 2 + delta_b ** 2)

# Ftiaxnei background gradient gia canvas
def create_gradient_background(canvas, width, height):
    for i in range(height):
        color_value = int(255 * (i / height))
        hex_color = f'#{color_value:02x}{color_value:02x}{color_value:02x}'
        canvas.create_rectangle(0, i, width, i + 1, outline=hex_color, fill=hex_color)

# Anoigei neo parathyro kai deixnei ta διορθωμένα χρώματα
def finish_app():
    result_window = Toplevel(root)
    result_window.title("Fixed Colors")

    result_canvas = Canvas(result_window, width=500, height=500)
    result_canvas.pack()

    create_gradient_background(result_canvas, 500, 500)

    y_offset = 10
    for (x, y), (original_color, fixed_color) in fixed_pixels.items():
        original_hex = f'#{original_color[0]:02x}{original_color[1]:02x}{original_color[2]:02x}'
        fixed_hex = f'#{fixed_color[0]:02x}{fixed_color[1]:02x}{fixed_color[2]:02x}'
        
        result_canvas.create_text(20, y_offset, anchor='w', text=f'Coords: ({x}, {y})', fill="black")
        result_canvas.create_text(150, y_offset, anchor='w', text=f'Original: {original_hex}', fill=original_hex)
        result_canvas.create_text(300, y_offset, anchor='w', text=f'Fixed: {fixed_hex}', fill=fixed_hex)
        
        y_offset += 20

# Arxikopoiisi tou parathyrou
root = Tk()
root.title("Color Extractor")

# Moderno style me ttk
ttk.Style().theme_use('clam')

button = ttk.Button(root, text="Διάλεξε Φωτογραφία", command=choose_file)
button.pack(pady=20)

fix_button = ttk.Button(root, text="FIX", command=fix_green_grids)
fix_button.pack(pady=20)

label = ttk.Label(root, text="", justify="left")
label.pack(pady=20)

canvas = Canvas(root, width=500, height=500)
canvas.pack(pady=20)

# Slider gia analogi tou megethous tis eikonas
scale = Scale(root, from_=50, to=500, orient=HORIZONTAL, label="Ανάλυση Εικόνας (px)")
scale.set(100)
scale.pack(pady=20)

# Label gia to epilegmeno xroma
chosen_color_label = ttk.Label(root, text="Επέλεξε χρώμα από το grid", justify="left")
chosen_color_label.pack(pady=20)

# Koumpi gia teliki emfanisi ton διορθώσεων
finish_button = ttk.Button(root, text="Τέλος", command=finish_app)
finish_button.pack(pady=20)

root.mainloop()
