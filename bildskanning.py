#!/usr/bin/env python3
"""
Bildskanning - Image Handling Program
Converts and edits negative images from DSLR scanning to positive images.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageOps, ImageEnhance
import os


class ImageHandlerApp:
    """Main application for handling and converting negative images."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Bildskanning - Negativ till Positiv")
        self.root.geometry("1000x700")
        
        # Image variables
        self.original_image = None
        self.current_image = None
        self.display_image = None
        self.photo_image = None
        self.is_inverted = False
        
        # Adjustment variables
        self.brightness_var = tk.DoubleVar(value=1.0)
        self.contrast_var = tk.DoubleVar(value=1.0)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fil", menu=file_menu)
        file_menu.add_command(label="Öppna bild...", command=self.load_image)
        file_menu.add_command(label="Spara bild...", command=self.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="Avsluta", command=self.root.quit)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Image display area
        image_frame = ttk.LabelFrame(main_frame, text="Bildbild", padding="10")
        image_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        self.image_label = ttk.Label(image_frame, text="Ingen bild laddad", anchor="center")
        self.image_label.pack(expand=True, fill=tk.BOTH)
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Kontroller", padding="10")
        control_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Load button
        load_btn = ttk.Button(control_frame, text="Ladda Bild", command=self.load_image)
        load_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Invert button
        self.invert_btn = ttk.Button(
            control_frame, 
            text="Konvertera till Positiv", 
            command=self.toggle_invert,
            state=tk.DISABLED
        )
        self.invert_btn.pack(fill=tk.X, pady=(0, 20))
        
        # Brightness control
        brightness_frame = ttk.LabelFrame(control_frame, text="Ljusstyrka", padding="5")
        brightness_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.brightness_label = ttk.Label(brightness_frame, text="1.0")
        self.brightness_label.pack()
        
        brightness_slider = ttk.Scale(
            brightness_frame,
            from_=0.5,
            to=2.0,
            orient=tk.HORIZONTAL,
            variable=self.brightness_var,
            command=self.update_brightness_label
        )
        brightness_slider.pack(fill=tk.X)
        
        brightness_apply = ttk.Button(
            brightness_frame,
            text="Applicera",
            command=self.apply_adjustments
        )
        brightness_apply.pack(fill=tk.X, pady=(5, 0))
        
        # Contrast control
        contrast_frame = ttk.LabelFrame(control_frame, text="Kontrast", padding="5")
        contrast_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.contrast_label = ttk.Label(contrast_frame, text="1.0")
        self.contrast_label.pack()
        
        contrast_slider = ttk.Scale(
            contrast_frame,
            from_=0.5,
            to=2.0,
            orient=tk.HORIZONTAL,
            variable=self.contrast_var,
            command=self.update_contrast_label
        )
        contrast_slider.pack(fill=tk.X)
        
        contrast_apply = ttk.Button(
            contrast_frame,
            text="Applicera",
            command=self.apply_adjustments
        )
        contrast_apply.pack(fill=tk.X, pady=(5, 0))
        
        # Reset button
        reset_btn = ttk.Button(
            control_frame,
            text="Återställ",
            command=self.reset_adjustments
        )
        reset_btn.pack(fill=tk.X, pady=(10, 0))
        
        # Save button
        save_btn = ttk.Button(
            control_frame,
            text="Spara Bild",
            command=self.save_image
        )
        save_btn.pack(fill=tk.X, pady=(20, 0))
        
        # Status bar
        self.status_var = tk.StringVar(value="Välkommen till Bildskanning")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
    def update_brightness_label(self, value):
        """Update brightness label with current value."""
        self.brightness_label.config(text=f"{float(value):.2f}")
        
    def update_contrast_label(self, value):
        """Update contrast label with current value."""
        self.contrast_label.config(text=f"{float(value):.2f}")
        
    def load_image(self):
        """Load an image file."""
        file_path = filedialog.askopenfilename(
            title="Välj en bild",
            filetypes=[
                ("Bildfiler", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Alla filer", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.original_image = Image.open(file_path)
                self.current_image = self.original_image.copy()
                self.is_inverted = False
                self.reset_adjustments()
                self.display_current_image()
                self.invert_btn.config(state=tk.NORMAL, text="Konvertera till Positiv")
                self.status_var.set(f"Bild laddad: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Fel", f"Kunde inte ladda bild: {str(e)}")
                
    def toggle_invert(self):
        """Toggle between negative and positive image."""
        if self.current_image is None:
            return
            
        if not self.is_inverted:
            # Convert negative to positive (invert)
            self.current_image = ImageOps.invert(self.original_image.convert('RGB'))
            self.is_inverted = True
            self.invert_btn.config(text="Konvertera till Negativ")
            self.status_var.set("Bild konverterad till positiv")
        else:
            # Convert back to negative (original)
            self.current_image = self.original_image.copy()
            self.is_inverted = False
            self.invert_btn.config(text="Konvertera till Positiv")
            self.status_var.set("Bild återställd till negativ")
            
        self.reset_adjustments()
        self.display_current_image()
        
    def apply_adjustments(self):
        """Apply brightness and contrast adjustments."""
        if self.current_image is None:
            return
            
        # Start with the current image (either inverted or original)
        if self.is_inverted:
            base_image = ImageOps.invert(self.original_image.convert('RGB'))
        else:
            base_image = self.original_image.copy()
            
        # Apply brightness
        brightness_enhancer = ImageEnhance.Brightness(base_image)
        adjusted_image = brightness_enhancer.enhance(self.brightness_var.get())
        
        # Apply contrast
        contrast_enhancer = ImageEnhance.Contrast(adjusted_image)
        adjusted_image = contrast_enhancer.enhance(self.contrast_var.get())
        
        self.current_image = adjusted_image
        self.display_current_image()
        self.status_var.set("Justeringar applicerade")
        
    def reset_adjustments(self):
        """Reset brightness and contrast to default values."""
        self.brightness_var.set(1.0)
        self.contrast_var.set(1.0)
        self.brightness_label.config(text="1.0")
        self.contrast_label.config(text="1.0")
        
        if self.current_image is not None:
            if self.is_inverted:
                self.current_image = ImageOps.invert(self.original_image.convert('RGB'))
            else:
                self.current_image = self.original_image.copy()
            self.display_current_image()
            self.status_var.set("Justeringar återställda")
        
    def display_current_image(self):
        """Display the current image in the GUI."""
        if self.current_image is None:
            return
            
        # Calculate display size while maintaining aspect ratio
        display_width = 600
        display_height = 600
        
        img_copy = self.current_image.copy()
        img_copy.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)
        
        self.photo_image = ImageTk.PhotoImage(img_copy)
        self.image_label.config(image=self.photo_image, text="")
        
    def save_image(self):
        """Save the current image to a file."""
        if self.current_image is None:
            messagebox.showwarning("Varning", "Ingen bild att spara")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Spara bild",
            defaultextension=".jpg",
            filetypes=[
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("TIFF", "*.tif *.tiff"),
                ("Alla filer", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.current_image.save(file_path)
                self.status_var.set(f"Bild sparad: {os.path.basename(file_path)}")
                messagebox.showinfo("Framgång", "Bilden har sparats!")
            except Exception as e:
                messagebox.showerror("Fel", f"Kunde inte spara bild: {str(e)}")


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = ImageHandlerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
