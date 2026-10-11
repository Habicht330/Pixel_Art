import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

PREVIEW_MAX = 650


class PixelArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер изображений в Pixel Art")
        self.root.geometry("1400x850")
        self.root.configure(bg="#f0f0f0")

        self.original_image = None
        self.preview_original = None

        self.tk_preview_original = None

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

        image_frame = tk.Frame(self.root, bg="#f0f0f0")
        image_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        left_frame = tk.Frame(image_frame, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            left_frame, text="Оригинал",
            font=("Arial", 12, "bold"), bg="#f0f0f0"
        ).pack()
        self.label_original = tk.Label(
            left_frame, bg="#ffffff", relief=tk.SUNKEN
        )
        self.label_original.pack(fill=tk.BOTH, expand=True, pady=5)

        right_frame = tk.Frame(image_frame, bg="#f0f0f0")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(
            right_frame, text="Pixel Art",
            font=("Arial", 12, "bold"), bg="#f0f0f0"
        ).pack()
        self.label_pixelated = tk.Label(
            right_frame, bg="#ffffff", relief=tk.SUNKEN
        )
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

            if img.mode != 'RGB':
                img = img.convert('RGB')

            self.original_image = img.copy()

            self.preview_original = img.copy()
            self.preview_original.thumbnail(
                (PREVIEW_MAX, PREVIEW_MAX), Image.Resampling.LANCZOS
            )

            w, h = self.original_image.size
            self.size_label.config(text=f"Размер: {w}×{h} px")

            self.tk_preview_original = ImageTk.PhotoImage(self.preview_original)
            self.label_original.config(image=self.tk_preview_original)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{e}")

    def save_image(self):
        messagebox.showinfo("Информация", "Функция сохранения будет добавлена позже")


if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtApp(root)
    root.mainloop()