import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import math

MAX_WIDTH = 1920
MAX_HEIGHT = 1080
PREVIEW_MAX = 650


def get_1d_weights(total_length, grid_count):
    ideal_step = total_length / grid_count
    weights_list = []
    for i in range(grid_count):
        start = i * ideal_step
        end = (i + 1) * ideal_step
        p_start = int(math.floor(start))
        p_end = int(math.ceil(end))

        block_weights = {}
        for p in range(p_start, p_end):
            overlap_start = max(float(p), start)
            overlap_end = min(float(p + 1), end)
            weight = overlap_end - overlap_start
            if weight > 0.001:
                block_weights[p] = weight
        weights_list.append(block_weights)
    return weights_list


def hybrid_pixelate_weighted(img, block_size):
    width, height = img.size
    if img.mode != 'RGB':
        img = img.convert('RGB')

    pixels = img.load()
    result = Image.new('RGB', (width, height))
    result_pixels = result.load()

    grid_w = (width + block_size - 1) // block_size
    grid_h = (height + block_size - 1) // block_size

    x_weights = get_1d_weights(width, grid_w)
    y_weights = get_1d_weights(height, grid_h)

    grid_colors = []
    for gy in range(grid_h):
        row_colors = []
        for gx in range(grid_w):
            total_r, total_g, total_b = 0.0, 0.0, 0.0
            total_weight = 0.0

            for y, weight_y in y_weights[gy].items():
                for x, weight_x in x_weights[gx].items():
                    pixel_weight = weight_x * weight_y
                    r, g, b = pixels[x, y]
                    total_r += r * pixel_weight
                    total_g += g * pixel_weight
                    total_b += b * pixel_weight
                    total_weight += pixel_weight

            if total_weight > 0:
                avg_color = (
                    int(round(total_r / total_weight)),
                    int(round(total_g / total_weight)),
                    int(round(total_b / total_weight))
                )
            else:
                avg_color = (0, 0, 0)
            row_colors.append(avg_color)
        grid_colors.append(row_colors)

    for gy in range(grid_h):
        for gx in range(grid_w):
            avg_color = grid_colors[gy][gx]
            x_start = gx * block_size
            y_start = gy * block_size
            x_end = min(x_start + block_size, width)
            y_end = min(y_start + block_size, height)

            for y in range(y_start, y_end):
                for x in range(x_start, x_end):
                    result_pixels[x, y] = avg_color
    return result


class PixelArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Art: Взвешенное усреднение")
        self.root.geometry("1400x850")
        self.root.configure(bg="#f0f0f0")

        self.original_image = None
        self.preview_original = None
        self.pixelated_full = None
        self.preview_pixelated = None

        self.tk_preview_original = None
        self.tk_preview_pixelated = None

        self.setup_ui()

    def setup_ui(self):
        control_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        control_frame.pack(fill=tk.X)

        self.btn_load = tk.Button(
            control_frame, text="Загрузить изображение", command=self.load_image,
            bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), padx=10
        )
        self.btn_load.pack(side=tk.LEFT, padx=20)

        self.btn_save = tk.Button(
            control_frame, text="Сохранить результат", command=self.save_image,
            bg="#2196F3", fg="white", font=("Arial", 10, "bold"), padx=10,
            state=tk.DISABLED
        )
        self.btn_save.pack(side=tk.LEFT, padx=20)

        self.size_label = tk.Label(
            control_frame, text="Изображение не загружено",
            bg="#f0f0f0", font=("Arial", 10), fg="#555"
        )
        self.size_label.pack(side=tk.RIGHT, padx=20)

        self.scale_label = tk.Label(
            control_frame, text="Размер блока: 10",
            bg="#f0f0f0", font=("Arial", 10)
        )
        self.scale_label.pack(side=tk.RIGHT, padx=20)

        self.pixel_scale = tk.Scale(
            control_frame, from_=1, to=50, orient=tk.HORIZONTAL,
            command=self.update_pixelation, bg="#f0f0f0", length=300
        )
        self.pixel_scale.set(10)
        self.pixel_scale.pack(side=tk.RIGHT, padx=10)

        image_frame = tk.Frame(self.root, bg="#f0f0f0")
        image_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        left_frame = tk.Frame(image_frame, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(left_frame, text="Оригинал", font=("Arial", 12, "bold"), bg="#f0f0f0").pack()
        self.label_original = tk.Label(left_frame, bg="#ffffff", relief=tk.SUNKEN)
        self.label_original.pack(fill=tk.BOTH, expand=True, pady=5)

        right_frame = tk.Frame(image_frame, bg="#f0f0f0")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(right_frame, text="Pixel Art (Взвешенный)", font=("Arial", 12, "bold"), bg="#f0f0f0").pack()
        self.label_pixelated = tk.Label(right_frame, bg="#ffffff", relief=tk.SUNKEN)
        self.label_pixelated.pack(fill=tk.BOTH, expand=True, pady=5)

    def load_image(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if not file_path:
            return

        try:
            img = Image.open(file_path)
            w, h = img.size

            if w > MAX_WIDTH or h > MAX_HEIGHT:
                img = img.resize((min(w, MAX_WIDTH), min(h, MAX_HEIGHT)), Image.Resampling.LANCZOS)
                new_w, new_h = img.size
                messagebox.showinfo("Изображение уменьшено", f"Исходный: {w}×{h}\nНовый: {new_w}×{new_h}")
                w, h = new_w, new_h

            if img.mode != 'RGB':
                img = img.convert('RGB')

            self.original_image = img.copy()
            self.preview_original = img.copy()
            self.preview_original.thumbnail((PREVIEW_MAX, PREVIEW_MAX), Image.Resampling.LANCZOS)

            self.size_label.config(text=f"Размер: {w}×{h} px")
            self.btn_save.config(state=tk.NORMAL)
            self.update_pixelation()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{e}")

    def update_pixelation(self, event=None):
        if self.original_image is None:
            return

        block_size = self.pixel_scale.get()
        self.scale_label.config(text=f"Размер блока: {block_size}")

        self.pixelated_full = hybrid_pixelate_weighted(self.original_image, block_size)

        self.preview_pixelated = self.pixelated_full.copy()
        self.preview_pixelated.thumbnail((PREVIEW_MAX, PREVIEW_MAX), Image.Resampling.NEAREST)

        self.tk_preview_original = ImageTk.PhotoImage(self.preview_original)
        self.tk_preview_pixelated = ImageTk.PhotoImage(self.preview_pixelated)

        self.label_original.config(image=self.tk_preview_original)
        self.label_pixelated.config(image=self.tk_preview_pixelated)

    def save_image(self):
        if self.pixelated_full is None:
            return

        file_path = filedialog.asksaveasfilename(
            title="Сохранить изображение",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.pixelated_full.save(file_path)
                w, h = self.pixelated_full.size
                messagebox.showinfo("Успех", f"Изображение успешно сохранено!\nРазмер: {w}×{h} px")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtApp(root)
    root.mainloop()