#!/usr/bin/env python3
"""
Bildskanning - Image Negative to Positive Converter
A simple MVP for converting and editing negative DSLR scans to positive images.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageOps, ImageEnhance
import os



class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Bildskanning - Negativ till Positiv Konvertering")
        self.root.geometry("1000x700")
        
        # Image variables
        self.original_image = None
        self.processed_image = None
        self.display_image = None
        self.current_file_path = None
        
        # Adjustment values
        self.brightness_value = 1.0
        self.contrast_value = 1.0
        self.is_inverted = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fil", menu=file_menu)
        file_menu.add_command(label="Öppna bild...", command=self.load_image)
        file_menu.add_command(label="Spara som...", command=self.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="Avsluta", command=self.root.quit)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Kontroller", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Load button
        ttk.Button(control_frame, text="Ladda bild", command=self.load_image).grid(
            row=0, column=0, padx=5, pady=5
        )
        
        # Invert button
        ttk.Button(control_frame, text="Konvertera till Positiv", command=self.toggle_invert).grid(
            row=0, column=1, padx=5, pady=5
        )
        
        # Reset button
        ttk.Button(control_frame, text="Återställ", command=self.reset_adjustments).grid(
            row=0, column=2, padx=5, pady=5
        )
        
        # Save button
        ttk.Button(control_frame, text="Spara bild", command=self.save_image).grid(
            row=0, column=3, padx=5, pady=5
        )
        
        # Brightness control
        ttk.Label(control_frame, text="Ljusstyrka:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.brightness_label = ttk.Label(control_frame, text="1.0")
        self.brightness_label.grid(row=1, column=3, padx=5, pady=5)
        self.brightness_scale = ttk.Scale(
            control_frame, from_=0.5, to=2.0, orient=tk.HORIZONTAL,
            command=self.on_brightness_change, length=150
        )
        self.brightness_scale.set(1.0)
        self.brightness_scale.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Contrast control
        ttk.Label(control_frame, text="Kontrast:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.contrast_label = ttk.Label(control_frame, text="1.0")
        self.contrast_label.grid(row=2, column=3, padx=5, pady=5)
        self.contrast_scale = ttk.Scale(
            control_frame, from_=0.5, to=2.0, orient=tk.HORIZONTAL,
            command=self.on_contrast_change, length=150
        )
        self.contrast_scale.set(1.0)
        self.contrast_scale.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Image display area
        image_frame = ttk.LabelFrame(main_frame, text="Bild", padding="10")
        image_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        image_frame.columnconfigure(0, weight=1)
        image_frame.rowconfigure(0, weight=1)
        
        # Canvas for image display
        self.canvas = tk.Canvas(image_frame, bg="gray", width=800, height=500)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        h_scrollbar = ttk.Scrollbar(image_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        v_scrollbar = ttk.Scrollbar(image_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Välkommen! Ladda en bild för att börja.", relief=tk.SUNKEN)
        self.status_label.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def load_image(self):
        """Load an image file"""
        file_path = filedialog.askopenfilename(
            title="Välj en bild",
            filetypes=[
                ("Bildfiler", "*.jpg *.jpeg *.png *.tif *.tiff *.bmp"),
                ("Alla filer", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.current_file_path = file_path
                self.original_image = Image.open(file_path)
                self.is_inverted = False
                self.reset_adjustments()
                self.update_status(f"Laddad: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Fel", f"Kunde inte ladda bilden: {str(e)}")
    
    def toggle_invert(self):
        """Toggle negative to positive conversion"""
        if self.original_image is None:
            messagebox.showwarning("Varning", "Ladda en bild först!")
            return
        
        self.is_inverted = not self.is_inverted
        self.apply_adjustments()
        
        status = "Konverterad till positiv" if self.is_inverted else "Återställd till original"
        self.update_status(status)
    
    def on_brightness_change(self, value):
        """Handle brightness slider change"""
        self.brightness_value = float(value)
        self.brightness_label.config(text=f"{self.brightness_value:.2f}")
        self.apply_adjustments()
    
    def on_contrast_change(self, value):
        """Handle contrast slider change"""
        self.contrast_value = float(value)
        self.contrast_label.config(text=f"{self.contrast_value:.2f}")
        self.apply_adjustments()
    
    def reset_adjustments(self):
        """Reset all adjustments to default"""
        self.brightness_scale.set(1.0)
        self.contrast_scale.set(1.0)
        self.brightness_value = 1.0
        self.contrast_value = 1.0
        self.is_inverted = False
        self.apply_adjustments()
        self.update_status("Justeringar återställda")
    
    def apply_adjustments(self):
        """Apply all adjustments to the image"""
        if self.original_image is None:
            return
        
        # Start with original image
        img = self.original_image.copy()
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Apply inversion (negative to positive)
        if self.is_inverted:
            img = ImageOps.invert(img)
        
        # Apply brightness adjustment
        if self.brightness_value != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(self.brightness_value)
        
        # Apply contrast adjustment
        if self.contrast_value != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(self.contrast_value)
        
        self.processed_image = img
        self.display_on_canvas()
    
    def display_on_canvas(self):
        """Display the processed image on canvas"""
        if self.processed_image is None:
            return
        
        # Calculate size to fit canvas while maintaining aspect ratio
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Use minimum size if canvas not yet rendered
        if canvas_width <= 1:
            canvas_width = 800
        if canvas_height <= 1:
            canvas_height = 500
        
        img = self.processed_image.copy()
        img.thumbnail((canvas_width - 20, canvas_height - 20), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        self.display_image = ImageTk.PhotoImage(img)
        
        # Clear canvas and display image
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width // 2, canvas_height // 2,
            image=self.display_image, anchor=tk.CENTER
        )
    
    def save_image(self):
        """Save the processed image"""
        if self.processed_image is None:
            messagebox.showwarning("Varning", "Ingen bild att spara!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Spara bild",
            defaultextension=".jpg",
            filetypes=[
                ("JPEG", "*.jpg"),
                ("PNG", "*.png"),
                ("TIFF", "*.tif"),
                ("Alla filer", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.processed_image.save(file_path)
                self.update_status(f"Sparad: {os.path.basename(file_path)}")
                messagebox.showinfo("Framgång", "Bilden sparades!")
            except Exception as e:
                messagebox.showerror("Fel", f"Kunde inte spara bilden: {str(e)}")
    
    def update_status(self, message):
        """Update the status bar"""
        self.status_label.config(text=message)


def main():
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
