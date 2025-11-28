#!/usr/bin/env python3
"""
Advanced Image Editor Module
Supports Color Negatives, B&W Negatives, and Positive Images
with professional-grade editing pipeline
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple
from pathlib import Path
import numpy as np
from PIL import Image
import cv2
import subprocess
import tempfile
import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QPushButton, QComboBox, QGroupBox, QScrollArea,
    QFileDialog, QMessageBox, QCheckBox, QDoubleSpinBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QRect, QPoint
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QMouseEvent
import sys


# ============================================================================
# INTERACTIVE IMAGE LABEL
# ============================================================================

class InteractiveImageLabel(QLabel):
    """Image label with mouse support for crop and white balance"""
    crop_selected = pyqtSignal(int, int, int, int)  # x, y, w, h
    white_balance_clicked = pyqtSignal(int, int)  # x, y
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_cropping = False
        self.is_white_balance_mode = False
        self.crop_start = None
        self.crop_current = None
        self.setMouseTracking(True)
    
    def start_crop_selection(self):
        """Enable crop selection mode"""
        self.is_cropping = True
        self.is_white_balance_mode = False
        self.crop_start = None
        self.crop_current = None
        self.setCursor(Qt.CursorShape.CrossCursor)
    
    def start_white_balance_selection(self):
        """Enable white balance selection mode"""
        self.is_white_balance_mode = True
        self.is_cropping = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def cancel_selection(self):
        """Cancel any selection mode"""
        self.is_cropping = False
        self.is_white_balance_mode = False
        self.crop_start = None
        self.crop_current = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_cropping:
                self.crop_start = event.pos()
                self.crop_current = event.pos()
            elif self.is_white_balance_mode:
                # Get position in image coordinates
                pos = event.pos()
                self.white_balance_clicked.emit(pos.x(), pos.y())
                self.cancel_selection()
        elif event.button() == Qt.MouseButton.RightButton:
            self.cancel_selection()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_cropping and self.crop_start is not None:
            self.crop_current = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.is_cropping:
            if self.crop_start is not None and self.crop_current is not None:
                # Calculate crop rectangle
                x1 = min(self.crop_start.x(), self.crop_current.x())
                y1 = min(self.crop_start.y(), self.crop_current.y())
                x2 = max(self.crop_start.x(), self.crop_current.x())
                y2 = max(self.crop_start.y(), self.crop_current.y())
                
                w = x2 - x1
                h = y2 - y1
                
                if w > 10 and h > 10:  # Minimum size
                    self.crop_selected.emit(x1, y1, w, h)
                
                self.cancel_selection()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        # Draw crop rectangle if active
        if self.is_cropping and self.crop_start is not None and self.crop_current is not None:
            painter = QPainter(self)
            pen = QPen(QColor(255, 255, 0), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            
            x1 = min(self.crop_start.x(), self.crop_current.x())
            y1 = min(self.crop_start.y(), self.crop_current.y())
            x2 = max(self.crop_start.x(), self.crop_current.x())
            y2 = max(self.crop_start.y(), self.crop_current.y())
            
            painter.drawRect(x1, y1, x2 - x1, y2 - y1)
            painter.end()


# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class ImageType(Enum):
    """Type of image being edited"""
    COLOR_NEGATIVE = "Color Negative"
    BW_NEGATIVE = "Black & White Negative"
    POSITIVE = "Positive"


class FilmProfile(Enum):
    """Film emulation profiles for color balance"""
    NEUTRAL = "Neutral"
    KODAK_PORTRA = "Kodak Portra"
    KODAK_EKTAR = "Kodak Ektar"
    FUJI_PRO = "Fuji Pro"
    FUJI_SUPERIA = "Fuji Superia"


class ToneCurveProfile(Enum):
    """Final tone curve profiles"""
    NEUTRAL = "Neutral"
    FRONTIER = "Frontier"
    NORITSU = "Noritsu"
    PORTRA_LIKE = "Portra-like"
    SOFT = "Soft"


@dataclass
class AutoEditParams:
    """Complete parameter set for the editing pipeline"""
    
    # Image type
    image_type: ImageType = ImageType.COLOR_NEGATIVE
    
    # Step 1: Histogram Normalization
    enable_histogram_centering: bool = True
    target_midpoint: float = 0.5
    mid_detection_method: str = "median"  # "mean" or "median"
    
    # Step 2: Black & White Point
    enable_bw_point: bool = True
    black_point_percentile: float = 0.5
    white_point_percentile: float = 99.5
    shadow_bias: float = 0.0
    highlight_bias: float = 0.0
    clip_protection: float = 0.02
    
    # Step 3: Midtone Correction
    enable_midtone: bool = True
    gamma: float = 1.0
    midtone_target: float = 0.5
    midtone_restore_strength: float = 0.0
    
    # Step 4: Dynamic Range Expansion
    enable_dynamic_range: bool = True
    toe_strength: float = 0.3
    shoulder_strength: float = 0.3
    midtone_contrast: float = 1.1
    
    # Step 5: Color Balance
    enable_color_balance: bool = True
    neutral_balance_strength: float = 0.5
    film_profile: FilmProfile = FilmProfile.NEUTRAL
    
    # White balance (custom)
    enable_white_balance: bool = False
    wb_temperature: float = 0.0  # -100 to 100 (blue to yellow)
    wb_tint: float = 0.0  # -100 to 100 (green to magenta)
    
    # Step 6: Local Contrast Smoothing
    enable_smoothing: bool = False
    smoothing_strength: float = 0.3
    shadow_smoothing: float = 0.5
    highlight_smoothing: float = 0.5
    preserve_edges: float = 0.7
    
    # Step 7: Saturation Adjustment
    enable_saturation: bool = True
    base_saturation: float = 1.0
    density_modulation_strength: float = 0.3
    shadow_color_boost: float = 0.1
    
    # Step 8: Highlight & Shadow Protection
    enable_protection: bool = True
    highlight_protection_strength: float = 0.3
    shadow_recovery_strength: float = 0.2
    
    # Step 9: Final Tone Curve
    enable_final_curve: bool = True
    final_curve_profile: ToneCurveProfile = ToneCurveProfile.NEUTRAL
    
    @classmethod
    def for_color_negative(cls) -> 'AutoEditParams':
        """Default parameters for color negatives"""
        return cls(
            image_type=ImageType.COLOR_NEGATIVE,
            enable_histogram_centering=True,
            target_midpoint=0.5,
            enable_bw_point=True,
            black_point_percentile=1.0,
            white_point_percentile=99.0,
            enable_midtone=True,
            gamma=1.1,
            enable_dynamic_range=True,
            toe_strength=0.4,
            shoulder_strength=0.35,
            midtone_contrast=1.15,
            enable_color_balance=True,
            neutral_balance_strength=0.6,
            film_profile=FilmProfile.KODAK_PORTRA,
            enable_saturation=True,
            base_saturation=1.1,
            density_modulation_strength=0.25,
            enable_final_curve=True,
            final_curve_profile=ToneCurveProfile.PORTRA_LIKE
        )
    
    @classmethod
    def for_bw_negative(cls) -> 'AutoEditParams':
        """Default parameters for B&W negatives"""
        return cls(
            image_type=ImageType.BW_NEGATIVE,
            enable_histogram_centering=True,
            target_midpoint=0.5,
            enable_bw_point=True,
            black_point_percentile=0.5,
            white_point_percentile=99.5,
            enable_midtone=True,
            gamma=1.05,
            enable_dynamic_range=True,
            toe_strength=0.3,
            shoulder_strength=0.3,
            midtone_contrast=1.1,
            enable_color_balance=False,
            enable_saturation=False,
            enable_smoothing=True,
            smoothing_strength=0.2,
            enable_final_curve=True,
            final_curve_profile=ToneCurveProfile.NEUTRAL
        )
    
    @classmethod
    def for_positive(cls) -> 'AutoEditParams':
        """Default parameters for positive images"""
        return cls(
            image_type=ImageType.POSITIVE,
            enable_histogram_centering=False,
            enable_bw_point=True,
            black_point_percentile=0.1,
            white_point_percentile=99.9,
            enable_midtone=True,
            gamma=1.0,
            enable_dynamic_range=False,
            enable_color_balance=True,
            neutral_balance_strength=0.3,
            enable_saturation=True,
            base_saturation=1.05,
            enable_final_curve=True,
            final_curve_profile=ToneCurveProfile.NEUTRAL
        )


# ============================================================================
# IMAGE PROCESSING PIPELINE
# ============================================================================

def apply_edit_pipeline(image: np.ndarray, params: AutoEditParams) -> np.ndarray:
    """
    Apply the complete editing pipeline to an image.
    
    Args:
        image: Input image as numpy array (uint8, RGB or grayscale)
        params: AutoEditParams containing all pipeline settings
    
    Returns:
        Processed image as numpy array (uint8)
    """
    # Convert to float32 [0, 1]
    img = image.astype(np.float32) / 255.0
    
    # Handle negative inversion first
    if params.image_type == ImageType.COLOR_NEGATIVE:
        img = _invert_color_negative(img)
    elif params.image_type == ImageType.BW_NEGATIVE:
        img = _invert_bw_negative(img)
    
    # Step 1: Histogram Normalization
    if params.enable_histogram_centering:
        img = _histogram_centering(img, params)
    
    # Step 2: Black & White Point
    if params.enable_bw_point:
        img = _apply_bw_point(img, params)
    
    # Step 3: Midtone Correction
    if params.enable_midtone:
        img = _apply_midtone_correction(img, params)
    
    # Step 4: Dynamic Range Expansion
    if params.enable_dynamic_range:
        img = _apply_dynamic_range(img, params)
    
    # Step 5: Color Balance (skip for B&W)
    if params.enable_color_balance and params.image_type != ImageType.BW_NEGATIVE:
        if len(img.shape) == 3 and img.shape[2] == 3:
            img = _apply_color_balance(img, params)
    
    # Step 6: Local Contrast Smoothing
    if params.enable_smoothing:
        img = _apply_smoothing(img, params)
    
    # Step 7: Saturation Adjustment (only for color images)
    if params.enable_saturation and params.image_type != ImageType.BW_NEGATIVE:
        if len(img.shape) == 3 and img.shape[2] == 3:
            img = _apply_saturation(img, params)
    
    # Step 8: Highlight & Shadow Protection
    if params.enable_protection:
        img = _apply_protection(img, params)
    
    # Step 9: Final Tone Curve
    if params.enable_final_curve:
        img = _apply_final_curve(img, params)
    
    # Clip and convert back to uint8
    img = np.clip(img, 0, 1)
    return (img * 255).astype(np.uint8)


# ============================================================================
# PIPELINE STEP IMPLEMENTATIONS
# ============================================================================

def _invert_color_negative(img: np.ndarray) -> np.ndarray:
    """Invert color negative with film base removal"""
    # Simple inversion
    inverted = 1.0 - img
    
    # Estimate and remove orange/brown film base
    # Find the darkest areas (which should be clear film)
    base_estimate = np.percentile(img, 95, axis=(0, 1))
    
    # Remove base color
    corrected = inverted - (1.0 - base_estimate)
    
    # Normalize
    min_val = np.percentile(corrected, 0.1)
    max_val = np.percentile(corrected, 99.9)
    
    if max_val > min_val:
        corrected = (corrected - min_val) / (max_val - min_val)
    
    return np.clip(corrected, 0, 1)


def _invert_bw_negative(img: np.ndarray) -> np.ndarray:
    """Invert B&W negative"""
    # Convert to grayscale if needed
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Simple inversion
    return 1.0 - img


def _histogram_centering(img: np.ndarray, params: AutoEditParams) -> np.ndarray:
    """Center histogram around target midpoint (optimized)"""
    # Always use mean (much faster than median)
    current_mid = np.mean(img)
    
    # Shift to target
    shift = params.target_midpoint - current_mid
    
    return np.clip(img + shift, 0, 1)


def _apply_bw_point(img: np.ndarray, params: AutoEditParams) -> np.ndarray:
    """Apply black and white point scaling"""
    # Calculate percentiles per channel
    if len(img.shape) == 3:
        black_point = np.percentile(img, params.black_point_percentile, axis=(0, 1))
        white_point = np.percentile(img, params.white_point_percentile, axis=(0, 1))
    else:
        black_point = np.percentile(img, params.black_point_percentile)
        white_point = np.percentile(img, params.white_point_percentile)
    
    # Apply biases
    black_point = black_point + params.shadow_bias
    white_point = white_point + params.highlight_bias
    
    # Apply clip protection
    black_point = np.clip(black_point, 0, params.clip_protection)
    white_point = np.clip(white_point, 1 - params.clip_protection, 1)
    
    # Scale
    if np.any(white_point > black_point):
        img = (img - black_point) / (white_point - black_point)
    
    return np.clip(img, 0, 1)


def _apply_midtone_correction(img: np.ndarray, params: AutoEditParams) -> np.ndarray:
    """Apply gamma correction to adjust midtones"""
    # Apply gamma
    if params.gamma != 1.0:
        img = np.power(img, 1.0 / params.gamma)
    
    # Optional: push midtones toward target
    if params.midtone_restore_strength > 0:
        current_mid = np.median(img)
        adjustment = (params.midtone_target - current_mid) * params.midtone_restore_strength
        img = img + adjustment
    
    return np.clip(img, 0, 1)


def _apply_dynamic_range(img: np.ndarray, params: AutoEditParams) -> np.ndarray:
    """Apply film-like toe and shoulder curves"""
    
    def toe_curve(x: np.ndarray, strength: float) -> np.ndarray:
        """Apply toe (shadow) curve"""
        if strength == 0:
            return x
        # Lift shadows slightly
        return x + strength * x * (1 - x) * (1 - x)
    
    def shoulder_curve(x: np.ndarray, strength: float) -> np.ndarray:
        """Apply shoulder (highlight) curve"""
        if strength == 0:
            return x
        # Compress highlights
        return x - strength * x * x * (1 - x)
    
    # Apply toe
    img = toe_curve(img, params.toe_strength)
    
    # Apply shoulder
    img = shoulder_curve(img, params.shoulder_strength)
    
    # Apply midtone contrast
    if params.midtone_contrast != 1.0:
        # S-curve around midpoint
        mid = 0.5
        img = mid + (img - mid) * params.midtone_contrast
    
    return np.clip(img, 0, 1)


def _apply_color_balance(img: np.ndarray, params: AutoEditParams) -> np.ndarray:
    """Apply color balance and film profile"""
    if len(img.shape) != 3 or img.shape[2] != 3:
        return img
    
    # Apply white balance first if enabled (temperature/tint model)
    if params.enable_white_balance and (params.wb_temperature != 0 or params.wb_tint != 0):
        # Temperature: -100 (cool/blue) to +100 (warm/yellow)
        # Tint: -100 (green) to +100 (magenta)
        
        temp_factor = params.wb_temperature / 100.0
        tint_factor = params.wb_tint / 100.0
        
        # Temperature adjustment (blue/yellow axis)
        if temp_factor > 0:  # Warmer (more yellow/red)
            img[:, :, 0] *= (1.0 + temp_factor * 0.3)  # Red up
            img[:, :, 2] *= (1.0 - temp_factor * 0.3)  # Blue down
        else:  # Cooler (more blue)
            img[:, :, 0] *= (1.0 + temp_factor * 0.3)  # Red down
            img[:, :, 2] *= (1.0 - temp_factor * 0.3)  # Blue up
        
        # Tint adjustment (green/magenta axis)
        if tint_factor > 0:  # More magenta
            img[:, :, 1] *= (1.0 - tint_factor * 0.3)  # Green down
        else:  # More green
            img[:, :, 1] *= (1.0 - tint_factor * 0.3)  # Green up
        
        img = np.clip(img, 0, 1)
    
    # Neutral gray balance - optimized
    if params.neutral_balance_strength > 0:
        # Use mean instead of median for speed (2-3x faster)
        gray_target = np.mean(img, axis=(0, 1))
        overall_gray = np.mean(gray_target)
        
        # Calculate correction
        correction = overall_gray / (gray_target + 1e-6)
        
        # Apply with strength
        correction = 1.0 + (correction - 1.0) * params.neutral_balance_strength
        img = img * correction
    
    # Apply film profile color shifts
    if params.film_profile == FilmProfile.KODAK_PORTRA:
        # Warmer tones, slightly boost reds and yellows
        img[:, :, 0] *= 1.02  # Red
        img[:, :, 1] *= 1.01  # Green
        img[:, :, 2] *= 0.98  # Blue
    elif params.film_profile == FilmProfile.KODAK_EKTAR:
        # Saturated, punchy colors
        img[:, :, 0] *= 1.03
        img[:, :, 2] *= 0.97
    elif params.film_profile == FilmProfile.FUJI_PRO:
        # Cooler tones, slight blue shift
        img[:, :, 0] *= 0.99
        img[:, :, 2] *= 1.02
    elif params.film_profile == FilmProfile.FUJI_SUPERIA:
        # Slightly warmer, green shift
        img[:, :, 1] *= 1.01
    
    return np.clip(img, 0, 1)


def _apply_smoothing(img: np.ndarray, params: AutoEditParams) -> np.ndarray:
    """Apply local contrast smoothing (optimized for speed)"""
    if params.smoothing_strength == 0:
        return img
    
    # Use fast Gaussian blur only (bilateral filter is too slow)
    # This is 50-100x faster than bilateral filter
    kernel_size = 5
    sigma = params.smoothing_strength * 3.0
    
    # Simple fast Gaussian blur
    smoothed = cv2.GaussianBlur(img, (kernel_size, kernel_size), sigma)
    
    return smoothed
    
    # Blend based on luminosity
    luminosity = np.mean(img, axis=2) if len(img.shape) == 3 else img
    
    # More smoothing in shadows and highlights
    shadow_mask = np.clip(1 - luminosity * 2, 0, 1) * params.shadow_smoothing
    highlight_mask = np.clip(luminosity * 2 - 1, 0, 1) * params.highlight_smoothing
    blend_mask = np.maximum(shadow_mask, highlight_mask)
    
    if len(img.shape) == 3:
        blend_mask = blend_mask[:, :, np.newaxis]
    
    result = img * (1 - blend_mask) + smoothed * blend_mask
    
    return np.clip(result, 0, 1)


def _apply_saturation(img: np.ndarray, params: AutoEditParams) -> np.ndarray:
    """Apply density-modulated saturation adjustment (optimized)"""
    if len(img.shape) != 3 or img.shape[2] != 3:
        return img
    
    # Fast saturation without HSV conversion (much faster)
    if params.base_saturation == 1.0 and params.density_modulation_strength == 0:
        return img  # Skip if no change
    
    # Calculate luminosity
    luminosity = img[:, :, 0] * 0.299 + img[:, :, 1] * 0.587 + img[:, :, 2] * 0.114
    luminosity = luminosity[:, :, np.newaxis]
    
    # Simple saturation adjustment (faster than HSV)
    # Move each channel toward/away from luminosity
    if params.base_saturation != 1.0:
        img = luminosity + (img - luminosity) * params.base_saturation
    
    # Apply density modulation if needed
    if params.density_modulation_strength > 0:
        density_factor = 1.0 + params.density_modulation_strength * (luminosity - 0.5)
        shadow_boost = np.clip(1 - luminosity, 0, 1) * params.shadow_color_boost
        density_factor += shadow_boost
        
        # Modulate distance from luminosity
        img = luminosity + (img - luminosity) * density_factor
    
    return np.clip(img, 0, 1)


def _apply_protection(img: np.ndarray, params: AutoEditParams) -> np.ndarray:
    """Protect highlights and recover shadow detail"""
    
    # Calculate luminosity
    if len(img.shape) == 3:
        luminosity = img[:, :, 0] * 0.299 + img[:, :, 1] * 0.587 + img[:, :, 2] * 0.114
    else:
        luminosity = img
    
    # Highlight protection - compress very bright areas
    if params.highlight_protection_strength > 0:
        highlight_mask = np.clip((luminosity - 0.8) / 0.2, 0, 1)
        highlight_mask = highlight_mask ** 2  # Smooth transition
        
        # Compress highlights
        compression = 1.0 - params.highlight_protection_strength * highlight_mask
        
        if len(img.shape) == 3:
            compression = compression[:, :, np.newaxis]
        
        img = img * compression + (1 - compression) * 0.95
    
    # Shadow recovery - lift very dark areas
    if params.shadow_recovery_strength > 0:
        shadow_mask = np.clip((0.2 - luminosity) / 0.2, 0, 1)
        shadow_mask = shadow_mask ** 2
        
        lift = params.shadow_recovery_strength * shadow_mask * 0.05
        
        if len(img.shape) == 3:
            lift = lift[:, :, np.newaxis]
        
        img = img + lift
    
    return np.clip(img, 0, 1)


def _apply_final_curve(img: np.ndarray, params: AutoEditParams) -> np.ndarray:
    """Apply final tone curve for specific look"""
    
    def neutral_curve(x):
        return x
    
    def frontier_curve(x):
        """Fuji Frontier scanner style - slightly lifted shadows"""
        return x + 0.05 * x * (1 - x)
    
    def noritsu_curve(x):
        """Noritsu scanner style - compressed highlights"""
        return x - 0.03 * x * x * (1 - x)
    
    def portra_curve(x):
        """Portra-like curve - smooth, lifted shadows, soft highlights"""
        # Gentle S-curve with lifted toe
        return 0.05 + 0.9 * (x + 0.1 * x * (1 - x) - 0.05 * x * x * (1 - x))
    
    def soft_curve(x):
        """Soft, low contrast curve"""
        return 0.1 + 0.8 * x
    
    # Select curve
    curve_map = {
        ToneCurveProfile.NEUTRAL: neutral_curve,
        ToneCurveProfile.FRONTIER: frontier_curve,
        ToneCurveProfile.NORITSU: noritsu_curve,
        ToneCurveProfile.PORTRA_LIKE: portra_curve,
        ToneCurveProfile.SOFT: soft_curve
    }
    
    curve_func = curve_map.get(params.final_curve_profile, neutral_curve)
    
    return np.clip(curve_func(img), 0, 1)


# ============================================================================
# PROCESSING THREAD
# ============================================================================

class ProcessingThread(QThread):
    """Background thread for image processing"""
    finished = pyqtSignal(object)  # Emits processed image
    
    def __init__(self, image: np.ndarray, params: AutoEditParams):
        super().__init__()
        self.image = image
        self.params = params
    
    def run(self):
        """Process image in background"""
        try:
            result = apply_edit_pipeline(self.image, self.params)
            self.finished.emit(result)
        except Exception as e:
            print(f"Processing error: {e}")
            self.finished.emit(None)


# ============================================================================
# PYQT6 USER INTERFACE
# ============================================================================

class ImageEditorWindow(QMainWindow):
    """Main window for the advanced image editor"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Image Editor - DSLR Scan Processing")
        self.setGeometry(100, 100, 1400, 900)
        
        # Image data
        self.original_image: Optional[np.ndarray] = None  # Full resolution
        self.proxy_image: Optional[np.ndarray] = None     # Downscaled for preview
        self.processed_image: Optional[np.ndarray] = None # Full res processed
        self.processed_proxy: Optional[np.ndarray] = None # Proxy processed
        self.current_file_path: Optional[str] = None
        
        # Rotation and crop state
        self.rotation_angle: float = 0.0  # Current rotation in degrees
        self.crop_rect: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h) or None
        self.pre_transform_image: Optional[np.ndarray] = None  # Original before rotation/crop
        
        # Interactive crop state
        self.is_cropping: bool = False
        self.crop_start_point: Optional[QPoint] = None
        self.crop_current_rect: Optional[QRect] = None
        self.display_scale: float = 1.0  # Scale factor from display to actual image
        
        # Performance settings
        self.use_proxy = True  # Use proxy for real-time preview
        self.proxy_max_dimension = 960  # Max size for proxy (smaller = faster)
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._do_process)
        self.is_processing = False
        
        # Caching for performance
        self.cached_inverted_proxy = None
        self.cached_inverted_full = None
        self.last_image_type = None
        self.pipeline_cache = {}  # Cache intermediate steps
        
        # Parameters
        self.params = AutoEditParams.for_color_negative()
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel: File list and preview
        left_panel = QVBoxLayout()
        
        # File controls
        file_controls = QHBoxLayout()
        load_btn = QPushButton("Load Image")
        load_btn.clicked.connect(self.load_image)
        save_btn = QPushButton("Save Image")
        save_btn.clicked.connect(self.save_image)
        file_controls.addWidget(load_btn)
        file_controls.addWidget(save_btn)
        file_controls.addStretch()
        left_panel.addLayout(file_controls)
        
        # Transform controls (rotation & crop)
        transform_group = QGroupBox("Rotation & Crop")
        transform_layout = QVBoxLayout()
        
        # Rotation controls
        rotate_layout = QHBoxLayout()
        rotate_layout.addWidget(QLabel("Rotate:"))
        
        rotate_ccw_90_btn = QPushButton("↶ 90°")
        rotate_ccw_90_btn.clicked.connect(lambda: self.rotate_image(-90))
        rotate_layout.addWidget(rotate_ccw_90_btn)
        
        rotate_cw_90_btn = QPushButton("↷ 90°")
        rotate_cw_90_btn.clicked.connect(lambda: self.rotate_image(90))
        rotate_layout.addWidget(rotate_cw_90_btn)
        
        rotate_180_btn = QPushButton("180°")
        rotate_180_btn.clicked.connect(lambda: self.rotate_image(180))
        rotate_layout.addWidget(rotate_180_btn)
        
        rotate_layout.addStretch()
        transform_layout.addLayout(rotate_layout)
        
        # Fine rotation
        fine_rotate_layout = QHBoxLayout()
        fine_rotate_layout.addWidget(QLabel("Fine Adjust:"))
        
        self.rotation_spin = QDoubleSpinBox()
        self.rotation_spin.setRange(-45, 45)
        self.rotation_spin.setSingleStep(0.1)
        self.rotation_spin.setValue(0)
        self.rotation_spin.setSuffix("°")
        self.rotation_spin.valueChanged.connect(self.on_fine_rotation_changed)
        fine_rotate_layout.addWidget(self.rotation_spin)
        
        fine_rotate_layout.addStretch()
        transform_layout.addLayout(fine_rotate_layout)
        
        # Crop controls
        crop_layout = QHBoxLayout()
        crop_layout.addWidget(QLabel("Crop:"))
        
        self.crop_btn = QPushButton("✂ Draw Crop Area")
        self.crop_btn.clicked.connect(self.start_interactive_crop)
        self.crop_btn.setEnabled(False)
        self.crop_btn.setToolTip("Click and drag on image to select crop area")
        crop_layout.addWidget(self.crop_btn)
        
        self.clear_crop_btn = QPushButton("Clear Crop")
        self.clear_crop_btn.clicked.connect(self.clear_crop)
        self.clear_crop_btn.setEnabled(False)
        crop_layout.addWidget(self.clear_crop_btn)
        
        crop_layout.addStretch()
        transform_layout.addLayout(crop_layout)
        
        # Reset transform
        reset_transform_layout = QHBoxLayout()
        reset_transform_btn = QPushButton("Reset All Transforms")
        reset_transform_btn.clicked.connect(self.reset_transforms)
        reset_transform_layout.addWidget(reset_transform_btn)
        reset_transform_layout.addStretch()
        transform_layout.addLayout(reset_transform_layout)
        
        transform_group.setLayout(transform_layout)
        left_panel.addWidget(transform_group)
        
        # Image preview (interactive)
        self.image_label = InteractiveImageLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(600, 400)
        self.image_label.setStyleSheet("border: 2px solid #ccc; background-color: #2b2b2b;")
        self.image_label.setScaledContents(False)
        self.image_label.crop_selected.connect(self.on_crop_selected)
        left_panel.addWidget(self.image_label, stretch=1)
        
        # Status and progress
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Load an image to start")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        status_layout.addWidget(self.status_label, stretch=1)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        left_panel.addWidget(status_widget)
        
        main_layout.addLayout(left_panel, stretch=2)
        
        # Right panel: Controls
        right_panel = self.create_control_panel()
        main_layout.addWidget(right_panel, stretch=1)
        
    def create_control_panel(self) -> QScrollArea:
        """Create the scrollable control panel"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(400)
        
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        
        # Image Type Selector
        type_group = QGroupBox("Image Type")
        type_layout = QVBoxLayout()
        
        self.image_type_combo = QComboBox()
        self.image_type_combo.addItems([t.value for t in ImageType])
        self.image_type_combo.currentTextChanged.connect(self.on_image_type_changed)
        type_layout.addWidget(self.image_type_combo)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply to Current")
        apply_btn.clicked.connect(self.process_image)
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(reset_btn)
        type_layout.addLayout(btn_layout)
        
        type_group.setLayout(type_layout)
        controls_layout.addWidget(type_group)
        
        # Performance options
        perf_group = QGroupBox("⚡ Performance")
        perf_layout = QVBoxLayout()
        
        self.proxy_checkbox = QCheckBox("Use Proxy for Preview (Recommended)")
        self.proxy_checkbox.setChecked(self.use_proxy)
        self.proxy_checkbox.setToolTip("Process smaller image for faster preview. Full resolution processed on save.")
        self.proxy_checkbox.toggled.connect(self.on_proxy_toggle)
        perf_layout.addWidget(self.proxy_checkbox)
        
        self.full_res_btn = QPushButton("🔍 Process Full Resolution Now")
        self.full_res_btn.clicked.connect(self.process_full_resolution)
        self.full_res_btn.setEnabled(False)
        self.full_res_btn.setToolTip("Process full resolution to ensure preview and export match perfectly")
        perf_layout.addWidget(self.full_res_btn)
        
        perf_group.setLayout(perf_layout)
        controls_layout.addWidget(perf_group)
        
        # Step 1: Histogram Centering
        self.hist_group = self.create_histogram_controls()
        controls_layout.addWidget(self.hist_group)
        
        # Step 2: Black & White Point
        self.bw_group = self.create_bw_point_controls()
        controls_layout.addWidget(self.bw_group)
        
        # Step 3: Midtone Correction
        self.midtone_group = self.create_midtone_controls()
        controls_layout.addWidget(self.midtone_group)
        
        # Step 4: Dynamic Range
        self.dynamic_group = self.create_dynamic_range_controls()
        controls_layout.addWidget(self.dynamic_group)
        
        # Step 5: Color Balance
        self.color_group = self.create_color_balance_controls()
        controls_layout.addWidget(self.color_group)
        
        # Step 6: Smoothing
        self.smooth_group = self.create_smoothing_controls()
        controls_layout.addWidget(self.smooth_group)
        
        # Step 7: Saturation
        self.sat_group = self.create_saturation_controls()
        controls_layout.addWidget(self.sat_group)
        
        # Step 8: Protection
        self.protect_group = self.create_protection_controls()
        controls_layout.addWidget(self.protect_group)
        
        # Step 9: Final Curve
        self.curve_group = self.create_final_curve_controls()
        controls_layout.addWidget(self.curve_group)
        
        controls_layout.addStretch()
        
        scroll_area.setWidget(controls_widget)
        return scroll_area
    
    def create_histogram_controls(self) -> QGroupBox:
        """Create histogram centering controls"""
        group = QGroupBox("1. Histogram Centering")
        group.setCheckable(True)
        group.setChecked(self.params.enable_histogram_centering)
        group.toggled.connect(lambda checked: self.update_param('enable_histogram_centering', checked))
        
        layout = QVBoxLayout()
        
        # Target midpoint
        layout.addWidget(QLabel("Target Midpoint:"))
        self.target_mid_slider = self.create_slider(0, 100, int(self.params.target_midpoint * 100),
                                                     lambda v: self.update_param('target_midpoint', v / 100))
        layout.addWidget(self.target_mid_slider)
        
        # Detection method
        layout.addWidget(QLabel("Detection Method:"))
        self.mid_method_combo = QComboBox()
        self.mid_method_combo.addItems(["mean", "median"])
        self.mid_method_combo.setCurrentText(self.params.mid_detection_method)
        self.mid_method_combo.currentTextChanged.connect(
            lambda v: self.update_param('mid_detection_method', v))
        layout.addWidget(self.mid_method_combo)
        
        group.setLayout(layout)
        return group
    
    def create_bw_point_controls(self) -> QGroupBox:
        """Create black & white point controls"""
        group = QGroupBox("2. Black & White Point")
        group.setCheckable(True)
        group.setChecked(self.params.enable_bw_point)
        group.toggled.connect(lambda checked: self.update_param('enable_bw_point', checked))
        
        layout = QVBoxLayout()
        
        # Black point percentile
        layout.addWidget(QLabel("Black Point Percentile:"))
        self.black_percentile_slider = self.create_slider(
            0, 50, int(self.params.black_point_percentile * 10),
            lambda v: self.update_param('black_point_percentile', v / 10))
        layout.addWidget(self.black_percentile_slider)
        
        # White point percentile
        layout.addWidget(QLabel("White Point Percentile:"))
        self.white_percentile_slider = self.create_slider(
            950, 1000, int(self.params.white_point_percentile * 10),
            lambda v: self.update_param('white_point_percentile', v / 10))
        layout.addWidget(self.white_percentile_slider)
        
        # Shadow bias
        layout.addWidget(QLabel("Shadow Bias:"))
        self.shadow_bias_slider = self.create_slider(
            -20, 20, int(self.params.shadow_bias * 100),
            lambda v: self.update_param('shadow_bias', v / 100))
        layout.addWidget(self.shadow_bias_slider)
        
        # Highlight bias
        layout.addWidget(QLabel("Highlight Bias:"))
        self.highlight_bias_slider = self.create_slider(
            -20, 20, int(self.params.highlight_bias * 100),
            lambda v: self.update_param('highlight_bias', v / 100))
        layout.addWidget(self.highlight_bias_slider)
        
        group.setLayout(layout)
        return group
    
    def create_midtone_controls(self) -> QGroupBox:
        """Create midtone correction controls"""
        group = QGroupBox("3. Midtone Correction (Gamma)")
        group.setCheckable(True)
        group.setChecked(self.params.enable_midtone)
        group.toggled.connect(lambda checked: self.update_param('enable_midtone', checked))
        
        layout = QVBoxLayout()
        
        # Gamma
        layout.addWidget(QLabel("Gamma:"))
        self.gamma_slider = self.create_slider(
            50, 200, int(self.params.gamma * 100),
            lambda v: self.update_param('gamma', v / 100))
        layout.addWidget(self.gamma_slider)
        
        # Midtone target
        layout.addWidget(QLabel("Midtone Target:"))
        self.midtone_target_slider = self.create_slider(
            0, 100, int(self.params.midtone_target * 100),
            lambda v: self.update_param('midtone_target', v / 100))
        layout.addWidget(self.midtone_target_slider)
        
        # Restore strength
        layout.addWidget(QLabel("Restore Strength:"))
        self.midtone_restore_slider = self.create_slider(
            0, 100, int(self.params.midtone_restore_strength * 100),
            lambda v: self.update_param('midtone_restore_strength', v / 100))
        layout.addWidget(self.midtone_restore_slider)
        
        group.setLayout(layout)
        return group
    
    def create_dynamic_range_controls(self) -> QGroupBox:
        """Create dynamic range expansion controls"""
        group = QGroupBox("4. Dynamic Range (Toe/Shoulder)")
        group.setCheckable(True)
        group.setChecked(self.params.enable_dynamic_range)
        group.toggled.connect(lambda checked: self.update_param('enable_dynamic_range', checked))
        
        layout = QVBoxLayout()
        
        # Toe strength
        layout.addWidget(QLabel("Toe Strength (Shadows):"))
        self.toe_slider = self.create_slider(
            0, 100, int(self.params.toe_strength * 100),
            lambda v: self.update_param('toe_strength', v / 100))
        layout.addWidget(self.toe_slider)
        
        # Shoulder strength
        layout.addWidget(QLabel("Shoulder Strength (Highlights):"))
        self.shoulder_slider = self.create_slider(
            0, 100, int(self.params.shoulder_strength * 100),
            lambda v: self.update_param('shoulder_strength', v / 100))
        layout.addWidget(self.shoulder_slider)
        
        # Midtone contrast
        layout.addWidget(QLabel("Midtone Contrast:"))
        self.midtone_contrast_slider = self.create_slider(
            50, 200, int(self.params.midtone_contrast * 100),
            lambda v: self.update_param('midtone_contrast', v / 100))
        layout.addWidget(self.midtone_contrast_slider)
        
        group.setLayout(layout)
        return group
    
    def create_color_balance_controls(self) -> QGroupBox:
        """Create color balance controls"""
        group = QGroupBox("5. Color Balance")
        group.setCheckable(True)
        group.setChecked(self.params.enable_color_balance)
        group.toggled.connect(lambda checked: self.update_param('enable_color_balance', checked))
        
        layout = QVBoxLayout()
        
        # White Balance controls
        wb_label = QLabel("White Balance:")
        wb_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(wb_label)
        
        # Temperature slider
        layout.addWidget(QLabel("Temperature (Blue ←→ Yellow):"))
        self.wb_temp_slider = self.create_slider(
            -100, 100, int(self.params.wb_temperature),
            lambda v: self.update_wb_temp(v))
        layout.addWidget(self.wb_temp_slider)
        
        # Tint slider
        layout.addWidget(QLabel("Tint (Green ←→ Magenta):"))
        self.wb_tint_slider = self.create_slider(
            -100, 100, int(self.params.wb_tint),
            lambda v: self.update_wb_tint(v))
        layout.addWidget(self.wb_tint_slider)
        
        # Neutral balance strength
        layout.addWidget(QLabel("Neutral Balance Strength:"))
        self.neutral_balance_slider = self.create_slider(
            0, 100, int(self.params.neutral_balance_strength * 100),
            lambda v: self.update_param('neutral_balance_strength', v / 100))
        layout.addWidget(self.neutral_balance_slider)
        
        # Film profile
        layout.addWidget(QLabel("Film Profile:"))
        self.film_profile_combo = QComboBox()
        self.film_profile_combo.addItems([p.value for p in FilmProfile])
        self.film_profile_combo.setCurrentText(self.params.film_profile.value)
        self.film_profile_combo.currentTextChanged.connect(self.on_film_profile_changed)
        layout.addWidget(self.film_profile_combo)
        
        group.setLayout(layout)
        return group
    
    def create_smoothing_controls(self) -> QGroupBox:
        """Create smoothing controls"""
        group = QGroupBox("6. Local Contrast Smoothing")
        group.setCheckable(True)
        group.setChecked(self.params.enable_smoothing)
        group.toggled.connect(lambda checked: self.update_param('enable_smoothing', checked))
        
        layout = QVBoxLayout()
        
        # Smoothing strength
        layout.addWidget(QLabel("Smoothing Strength:"))
        self.smooth_strength_slider = self.create_slider(
            0, 100, int(self.params.smoothing_strength * 100),
            lambda v: self.update_param('smoothing_strength', v / 100))
        layout.addWidget(self.smooth_strength_slider)
        
        # Shadow smoothing
        layout.addWidget(QLabel("Shadow Smoothing:"))
        self.shadow_smooth_slider = self.create_slider(
            0, 100, int(self.params.shadow_smoothing * 100),
            lambda v: self.update_param('shadow_smoothing', v / 100))
        layout.addWidget(self.shadow_smooth_slider)
        
        # Highlight smoothing
        layout.addWidget(QLabel("Highlight Smoothing:"))
        self.highlight_smooth_slider = self.create_slider(
            0, 100, int(self.params.highlight_smoothing * 100),
            lambda v: self.update_param('highlight_smoothing', v / 100))
        layout.addWidget(self.highlight_smooth_slider)
        
        # Edge preservation
        layout.addWidget(QLabel("Preserve Edges:"))
        self.preserve_edges_slider = self.create_slider(
            0, 100, int(self.params.preserve_edges * 100),
            lambda v: self.update_param('preserve_edges', v / 100))
        layout.addWidget(self.preserve_edges_slider)
        
        group.setLayout(layout)
        return group
    
    def create_saturation_controls(self) -> QGroupBox:
        """Create saturation controls"""
        group = QGroupBox("7. Saturation Adjustment")
        group.setCheckable(True)
        group.setChecked(self.params.enable_saturation)
        group.toggled.connect(lambda checked: self.update_param('enable_saturation', checked))
        
        layout = QVBoxLayout()
        
        # Base saturation
        layout.addWidget(QLabel("Base Saturation:"))
        self.base_sat_slider = self.create_slider(
            0, 200, int(self.params.base_saturation * 100),
            lambda v: self.update_param('base_saturation', v / 100))
        layout.addWidget(self.base_sat_slider)
        
        # Density modulation
        layout.addWidget(QLabel("Density Modulation:"))
        self.density_mod_slider = self.create_slider(
            0, 100, int(self.params.density_modulation_strength * 100),
            lambda v: self.update_param('density_modulation_strength', v / 100))
        layout.addWidget(self.density_mod_slider)
        
        # Shadow color boost
        layout.addWidget(QLabel("Shadow Color Boost:"))
        self.shadow_color_slider = self.create_slider(
            0, 50, int(self.params.shadow_color_boost * 100),
            lambda v: self.update_param('shadow_color_boost', v / 100))
        layout.addWidget(self.shadow_color_slider)
        
        group.setLayout(layout)
        return group
    
    def create_protection_controls(self) -> QGroupBox:
        """Create highlight & shadow protection controls"""
        group = QGroupBox("8. Highlight & Shadow Protection")
        group.setCheckable(True)
        group.setChecked(self.params.enable_protection)
        group.toggled.connect(lambda checked: self.update_param('enable_protection', checked))
        
        layout = QVBoxLayout()
        
        # Highlight protection
        layout.addWidget(QLabel("Highlight Protection:"))
        self.highlight_protect_slider = self.create_slider(
            0, 100, int(self.params.highlight_protection_strength * 100),
            lambda v: self.update_param('highlight_protection_strength', v / 100))
        layout.addWidget(self.highlight_protect_slider)
        
        # Shadow recovery
        layout.addWidget(QLabel("Shadow Recovery:"))
        self.shadow_recover_slider = self.create_slider(
            0, 100, int(self.params.shadow_recovery_strength * 100),
            lambda v: self.update_param('shadow_recovery_strength', v / 100))
        layout.addWidget(self.shadow_recover_slider)
        
        group.setLayout(layout)
        return group
    
    def create_final_curve_controls(self) -> QGroupBox:
        """Create final tone curve controls"""
        group = QGroupBox("9. Final Tone Curve")
        group.setCheckable(True)
        group.setChecked(self.params.enable_final_curve)
        group.toggled.connect(lambda checked: self.update_param('enable_final_curve', checked))
        
        layout = QVBoxLayout()
        
        # Curve profile
        layout.addWidget(QLabel("Curve Profile:"))
        self.curve_profile_combo = QComboBox()
        self.curve_profile_combo.addItems([p.value for p in ToneCurveProfile])
        self.curve_profile_combo.setCurrentText(self.params.final_curve_profile.value)
        self.curve_profile_combo.currentTextChanged.connect(self.on_curve_profile_changed)
        layout.addWidget(self.curve_profile_combo)
        
        group.setLayout(layout)
        return group
    
    def create_slider(self, min_val: int, max_val: int, initial: int, callback) -> QSlider:
        """Helper to create a slider with value label"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(initial)
        
        value_label = QLabel(f"{initial / 100:.2f}" if max_val > 10 else f"{initial}")
        value_label.setMinimumWidth(50)
        
        def on_change(value):
            display_val = value / 100 if max_val > 10 else value
            value_label.setText(f"{display_val:.2f}")
            callback(value)
            self.process_image()
        
        slider.valueChanged.connect(on_change)
        
        layout.addWidget(slider)
        layout.addWidget(value_label)
        
        # Return the container widget, but we need to return slider
        # Store value_label as slider attribute for later access
        slider.value_label = value_label
        slider.container = container
        
        return container
    
    def update_param(self, param_name: str, value):
        """Update a parameter and reprocess"""
        setattr(self.params, param_name, value)
        self.process_image()
    
    def on_image_type_changed(self, text: str):
        """Handle image type change"""
        # Map text to enum
        type_map = {t.value: t for t in ImageType}
        self.params.image_type = type_map[text]
        
        # Load appropriate defaults
        if self.params.image_type == ImageType.COLOR_NEGATIVE:
            self.params = AutoEditParams.for_color_negative()
        elif self.params.image_type == ImageType.BW_NEGATIVE:
            self.params = AutoEditParams.for_bw_negative()
        else:
            self.params = AutoEditParams.for_positive()
        
        # Update UI to reflect new params
        self.update_ui_from_params()
        self.process_image()
    
    def update_wb_temp(self, value: int):
        """Update white balance temperature"""
        self.params.wb_temperature = float(value)
        if value != 0 or self.params.wb_tint != 0:
            self.params.enable_white_balance = True
        else:
            self.params.enable_white_balance = False
        self.process_image()
    
    def update_wb_tint(self, value: int):
        """Update white balance tint"""
        self.params.wb_tint = float(value)
        if value != 0 or self.params.wb_temperature != 0:
            self.params.enable_white_balance = True
        else:
            self.params.enable_white_balance = False
        self.process_image()
    
    def on_film_profile_changed(self, text: str):
        """Handle film profile change"""
        profile_map = {p.value: p for p in FilmProfile}
        self.params.film_profile = profile_map[text]
        self.process_image()
    
    def on_curve_profile_changed(self, text: str):
        """Handle curve profile change"""
        curve_map = {p.value: p for p in ToneCurveProfile}
        self.params.final_curve_profile = curve_map[text]
        self.process_image()
    
    def update_ui_from_params(self):
        """Update all UI controls to match current params"""
        # Update checkboxes
        self.hist_group.setChecked(self.params.enable_histogram_centering)
        self.bw_group.setChecked(self.params.enable_bw_point)
        self.midtone_group.setChecked(self.params.enable_midtone)
        self.dynamic_group.setChecked(self.params.enable_dynamic_range)
        self.color_group.setChecked(self.params.enable_color_balance)
        self.smooth_group.setChecked(self.params.enable_smoothing)
        self.sat_group.setChecked(self.params.enable_saturation)
        self.protect_group.setChecked(self.params.enable_protection)
        self.curve_group.setChecked(self.params.enable_final_curve)
        
        # Disable color balance and saturation for B&W
        is_bw = self.params.image_type == ImageType.BW_NEGATIVE
        self.color_group.setEnabled(not is_bw)
        self.sat_group.setEnabled(not is_bw)
    
    def reset_to_defaults(self):
        """Reset parameters to defaults for current image type"""
        if self.params.image_type == ImageType.COLOR_NEGATIVE:
            self.params = AutoEditParams.for_color_negative()
        elif self.params.image_type == ImageType.BW_NEGATIVE:
            self.params = AutoEditParams.for_bw_negative()
        else:
            self.params = AutoEditParams.for_positive()
        
        self.update_ui_from_params()
        self.process_image()
    
    def reset_to_defaults(self):
        """Reset parameters to defaults for current image type"""
        if self.params.image_type == ImageType.COLOR_NEGATIVE:
            self.params = AutoEditParams.for_color_negative()
        elif self.params.image_type == ImageType.BW_NEGATIVE:
            self.params = AutoEditParams.for_bw_negative()
        else:
            self.params = AutoEditParams.for_positive()
        
        self.update_ui_from_params()
        self.process_image()
    
    def start_interactive_crop(self):
        """Start interactive crop mode"""
        if self.original_image is None:
            return
        
        self.image_label.start_crop_selection()
        self.status_label.setText("✂ Draw crop area with mouse (right-click to cancel)")
    
    def on_crop_selected(self, x: int, y: int, w: int, h: int):
        """Handle crop area selected by user"""
        # Convert from display coordinates to image coordinates
        if self.processed_proxy is None:
            return
        
        # Get the actual displayed image size and position
        pixmap = self.image_label.pixmap()
        if pixmap is None:
            return
        
        label_w = self.image_label.width()
        label_h = self.image_label.height()
        pixmap_w = pixmap.width()
        pixmap_h = pixmap.height()
        
        # Calculate offset (pixmap is centered in label)
        offset_x = (label_w - pixmap_w) // 2
        offset_y = (label_h - pixmap_h) // 2
        
        # Adjust coordinates
        x = x - offset_x
        y = y - offset_y
        
        # Check if within bounds
        if x < 0 or y < 0 or x + w > pixmap_w or y + h > pixmap_h:
            self.status_label.setText("⚠ Crop area outside image bounds")
            return
        
        # Scale to original image coordinates
        img_h, img_w = self.original_image.shape[:2]
        scale_x = img_w / pixmap_w
        scale_y = img_h / pixmap_h
        
        orig_x = int(x * scale_x)
        orig_y = int(y * scale_y)
        orig_w = int(w * scale_x)
        orig_h = int(h * scale_y)
        
        # Store pre-transform if first crop
        if self.pre_transform_image is None:
            self.pre_transform_image = self.original_image.copy()
        
        # Set crop rectangle
        self.crop_rect = (orig_x, orig_y, orig_w, orig_h)
        self.clear_crop_btn.setEnabled(True)
        
        # Apply transforms
        self._apply_transforms()
    

    
    def rotate_image(self, angle: float):
        """Rotate the image by specified angle"""
        if self.original_image is None:
            return
        
        # Store pre-transform if first rotation
        if self.pre_transform_image is None:
            self.pre_transform_image = self.original_image.copy()
        
        # Update rotation angle
        self.rotation_angle = (self.rotation_angle + angle) % 360
        
        # Apply rotation to pre-transform image
        self._apply_transforms()
    
    def on_fine_rotation_changed(self, angle: float):
        """Handle fine rotation adjustment"""
        if self.original_image is None:
            return
        
        # Store pre-transform if first rotation
        if self.pre_transform_image is None:
            self.pre_transform_image = self.original_image.copy()
        
        # Set exact angle
        self.rotation_angle = angle
        
        # Apply rotation
        self._apply_transforms()
    
    def start_interactive_crop(self):
        """Start interactive crop mode"""
        if self.original_image is None:
            return
        
        self.image_label.start_crop_selection()
        self.status_label.setText("✂ Draw crop area with mouse (right-click to cancel)")
    
    def clear_crop(self):
        """Clear crop area"""
        self.crop_rect = None
        self.clear_crop_btn.setEnabled(False)
        self._apply_transforms()
    
    def reset_transforms(self):
        """Reset all rotation and crop transforms"""
        if self.pre_transform_image is None:
            return
        
        # Reset state
        self.rotation_angle = 0.0
        self.crop_rect = None
        self.rotation_spin.setValue(0)
        self.clear_crop_btn.setEnabled(False)
        
        # Restore original
        self.original_image = self.pre_transform_image.copy()
        self.pre_transform_image = None
        
        # Recreate proxy and reprocess
        self.proxy_image = self._create_proxy(self.original_image)
        self.cached_inverted_proxy = None
        self.cached_inverted_full = None
        
        self.process_image()
        self.status_label.setText("Transforms reset")
    
    def _apply_transforms(self):
        """Apply rotation and crop to pre-transform image"""
        if self.pre_transform_image is None:
            return
        
        # Start with pre-transform image
        transformed = self.pre_transform_image.copy()
        
        # Apply rotation
        if self.rotation_angle != 0:
            h, w = transformed.shape[:2]
            center = (w // 2, h // 2)
            
            # Get rotation matrix
            M = cv2.getRotationMatrix2D(center, self.rotation_angle, 1.0)
            
            # Calculate new bounding box
            cos = np.abs(M[0, 0])
            sin = np.abs(M[0, 1])
            new_w = int(h * sin + w * cos)
            new_h = int(h * cos + w * sin)
            
            # Adjust translation
            M[0, 2] += (new_w - w) / 2
            M[1, 2] += (new_h - h) / 2
            
            # Rotate
            transformed = cv2.warpAffine(transformed, M, (new_w, new_h), 
                                        borderMode=cv2.BORDER_CONSTANT, 
                                        borderValue=(255, 255, 255) if len(transformed.shape) == 3 else 255)
        
        # Apply crop
        if self.crop_rect is not None:
            x, y, w, h = self.crop_rect
            img_h, img_w = transformed.shape[:2]
            
            # Validate and clip crop rect
            x = max(0, min(x, img_w - 1))
            y = max(0, min(y, img_h - 1))
            w = max(1, min(w, img_w - x))
            h = max(1, min(h, img_h - y))
            
            # Crop
            transformed = transformed[y:y+h, x:x+w]
        
        # Update original and proxy
        self.original_image = transformed
        self.proxy_image = self._create_proxy(transformed)
        
        # Clear cache since we transformed
        self.cached_inverted_proxy = None
        self.cached_inverted_full = None
        
        # Reprocess
        self.process_image()
        
        status = f"Rotated: {self.rotation_angle:.1f}°"
        if self.crop_rect:
            status += f" | Cropped: {w}x{h}"
        self.status_label.setText(status)
    
    def load_image(self):
        """Load an image file including RAW formats"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Image",
            "",
            "All Supported (*.jpg *.jpeg *.png *.tif *.tiff *.bmp *.arw *.cr2 *.nef *.dng);;"
            "RAW Files (*.arw *.cr2 *.nef *.dng *.raw);;"
            "Image Files (*.jpg *.jpeg *.png *.tif *.tiff *.bmp);;"
            "All Files (*.*)"
        )
        
        if file_path:
            try:
                self.status_label.setText("Loading...")
                QApplication.processEvents()
                
                # Check if RAW file
                file_ext = Path(file_path).suffix.lower()
                is_raw = file_ext in ['.arw', '.cr2', '.nef', '.dng', '.raw', '.raf', '.orf']
                
                if is_raw:
                    # Try multiple methods to load RAW file
                    pil_image = None
                    error_messages = []
                    
                    # Method 1: Try dcraw if available (best quality)
                    dcraw_path = Path(__file__).parent / "dcraw.exe"
                    if dcraw_path.exists():
                        try:
                            # Create temporary file for output
                            with tempfile.NamedTemporaryFile(suffix='.tiff', delete=False) as tmp:
                                tmp_path = tmp.name
                            
                            # Run dcraw to convert ARW to TIFF
                            # -T = TIFF output, -w = camera white balance, -q 3 = high quality
                            result = subprocess.run(
                                [str(dcraw_path), '-T', '-w', '-q', '3', '-o', '1', file_path],
                                capture_output=True,
                                text=True,
                                timeout=30
                            )
                            
                            # dcraw creates output next to input file
                            dcraw_output = Path(file_path).with_suffix('.tiff')
                            
                            if dcraw_output.exists():
                                pil_image = Image.open(dcraw_output)
                                # Clean up
                                os.unlink(dcraw_output)
                                
                                if pil_image.mode != 'RGB':
                                    pil_image = pil_image.convert('RGB')
                                    
                                self.status_label.setText(f"✓ Loaded RAW with dcraw: {Path(file_path).name}")
                        except Exception as e:
                            error_messages.append(f"dcraw: {str(e)}")
                    
                    # Method 2: Try PIL with WIC codec (requires codec pack)
                    if pil_image is None:
                        try:
                            pil_image = Image.open(file_path)
                            
                            # Get embedded JPEG preview if available
                            if hasattr(pil_image, 'n_frames') and pil_image.n_frames > 0:
                                pil_image.seek(0)
                            
                            if pil_image.mode != 'RGB':
                                pil_image = pil_image.convert('RGB')
                                
                        except Exception as e:
                            error_messages.append(f"PIL/WIC: {str(e)}")
                    
                    # If all methods failed, show error
                    if pil_image is None:
                        QMessageBox.critical(self, "Cannot Load RAW File", 
                            f"Failed to open Sony ARW file.\n\n"
                            f"Solutions:\n"
                            f"1. Run setup_arw_support.bat to download dcraw.exe\n"
                            f"2. Install Microsoft Camera Codec Pack\n"
                            f"3. Convert to TIFF first with Lightroom/Camera Raw\n\n"
                            f"Errors:\n" + "\n".join(error_messages))
                        self.status_label.setText("⚠ Cannot load ARW - see error message")
                        return
                else:
                    # Load regular image with PIL
                    pil_image = Image.open(file_path)
                    
                    # Convert to RGB if needed
                    if pil_image.mode != 'RGB':
                        pil_image = pil_image.convert('RGB')
                
                self.original_image = np.array(pil_image)
                self.current_file_path = file_path
                
                # Reset transforms
                self.rotation_angle = 0.0
                self.crop_rect = None
                self.pre_transform_image = None
                self.rotation_spin.setValue(0)
                self.clear_crop_btn.setEnabled(False)
                
                # Create proxy image for fast preview
                self.proxy_image = self._create_proxy(self.original_image)
                
                # Clear processed images and cache
                self.processed_image = None
                self.processed_proxy = None
                self.cached_inverted_proxy = None
                self.cached_inverted_full = None
                
                # Enable buttons
                self.full_res_btn.setEnabled(True)
                self.crop_btn.setEnabled(True)
                
                img_size = self.original_image.shape
                proxy_size = self.proxy_image.shape
                
                reduction = 100 * (1 - (proxy_size[0] * proxy_size[1]) / (img_size[0] * img_size[1]))
                
                file_type = "RAW" if is_raw else "Image"
                self.status_label.setText(
                    f"Loaded {file_type}: {Path(file_path).name} | "
                    f"Full: {img_size[1]}x{img_size[0]} | "
                    f"Proxy: {proxy_size[1]}x{proxy_size[0]} ({reduction:.0f}% smaller)"
                )
                
                self.process_image()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
                self.status_label.setText("Error loading image")
    
    def _create_proxy(self, image: np.ndarray) -> np.ndarray:
        """Create a downscaled proxy image for faster processing"""
        h, w = image.shape[:2]
        max_dim = max(h, w)
        
        if max_dim <= self.proxy_max_dimension:
            return image.copy()  # Already small enough
        
        # Calculate scale factor
        scale = self.proxy_max_dimension / max_dim
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize using PIL for quality
        pil_img = Image.fromarray(image)
        pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        return np.array(pil_img)
    
    def on_proxy_toggle(self, checked: bool):
        """Toggle proxy mode"""
        self.use_proxy = checked
        self.status_label.setText(f"Proxy mode: {'ON' if checked else 'OFF'}")
        if self.original_image is not None:
            # Reprocess with new mode
            self.process_image()
    
    def process_full_resolution(self):
        """Process full resolution image (for final review/save)"""
        if self.original_image is None:
            return
        
        reply = QMessageBox.question(
            self,
            "Process Full Resolution",
            f"This will process the full resolution image:\n"
            f"{self.original_image.shape[1]}x{self.original_image.shape[0]} pixels\n\n"
            f"This may take 5-30 seconds depending on image size.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.status_label.setText("🔄 Processing full resolution... Please wait...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate
            QApplication.processEvents()
            
            # Process full resolution (synchronously for simplicity)
            try:
                self.processed_image = apply_edit_pipeline(self.original_image, self.params)
                self.progress_bar.setVisible(False)
                self.status_label.setText("✅ Full resolution processing complete! Ready to save.")
                QMessageBox.information(self, "Complete", 
                    f"Full resolution processing complete!\n"
                    f"Resolution: {self.processed_image.shape[1]}x{self.processed_image.shape[0]}\n\n"
                    f"You can now save the image.")
            except Exception as e:
                self.progress_bar.setVisible(False)
                self.status_label.setText(f"Error: {str(e)}")
                QMessageBox.critical(self, "Error", f"Processing failed: {str(e)}")
    
    def save_image(self):
        """Save the processed image"""
        if self.processed_image is None and self.processed_proxy is None:
            QMessageBox.warning(self, "Warning", "No image to save!")
            return
        
        # Check if full res has been processed
        if self.processed_image is None:
            reply = QMessageBox.question(
                self,
                "Process Full Resolution?",
                "Full resolution version needs processing.\n"
                "This will ensure saved image matches preview.\n\n"
                "Process now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return
            
            # Process full resolution first
            self.status_label.setText("🔄 Processing full resolution for save...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            QApplication.processEvents()
            
            try:
                self.processed_image = apply_edit_pipeline(self.original_image, self.params)
                self.progress_bar.setVisible(False)
                self.status_label.setText("✓ Full resolution processed")
            except Exception as e:
                self.progress_bar.setVisible(False)
                QMessageBox.critical(self, "Error", f"Processing failed: {str(e)}")
                return
        
        # Save full resolution image
        image_to_save = self.processed_image
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "",
            "JPEG (*.jpg);;PNG (*.png);;TIFF (*.tif);;All Files (*.*)"
        )
        
        if file_path:
            try:
                # Convert numpy to PIL and save
                # Ensure RGB mode for color images
                if len(image_to_save.shape) == 3:
                    pil_image = Image.fromarray(image_to_save, mode='RGB')
                else:
                    pil_image = Image.fromarray(image_to_save, mode='L')
                
                # Save with appropriate quality
                if file_path.lower().endswith(('.jpg', '.jpeg')):
                    pil_image.save(file_path, quality=95, subsampling=0)
                elif file_path.lower().endswith('.png'):
                    pil_image.save(file_path, compress_level=3)
                else:
                    pil_image.save(file_path)
                
                saved_size = image_to_save.shape
                self.status_label.setText(f"💾 Saved: {Path(file_path).name} ({saved_size[1]}x{saved_size[0]})")
                QMessageBox.information(self, "Success", 
                    f"Image saved successfully!\nResolution: {saved_size[1]}x{saved_size[0]}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save image: {str(e)}")
    
    def process_image(self):
        """Process the image with current parameters (with debouncing)"""
        if self.original_image is None:
            return
        
        # Cancel any pending processing
        self.debounce_timer.stop()
        
        # Debounce: wait 150ms before processing (reduces lag during slider dragging)
        self.debounce_timer.start(150)
    
    def _do_process(self):
        """Actually process the image (optimized with caching)"""
        if self.is_processing:
            return
        
        try:
            self.is_processing = True
            
            # Always process BOTH proxy and full resolution to ensure consistency
            # Proxy for preview
            if self.proxy_image is not None:
                result_proxy = apply_edit_pipeline(self.proxy_image, self.params)
                self.processed_proxy = result_proxy
            
            # Full resolution for export (process in background if large)
            if self.original_image is not None:
                img_size = self.original_image.shape[0] * self.original_image.shape[1]
                
                # Only process full res immediately if image is small (<5MP)
                # Otherwise mark for processing before save
                if img_size < 5_000_000:
                    result_full = apply_edit_pipeline(self.original_image, self.params)
                    self.processed_image = result_full
                else:
                    # Mark that full res needs reprocessing (will process on save)
                    self.processed_image = None
            
            # Display
            self.display_image()
            
            mode = "proxy" if self.use_proxy else "full res"
            sync_status = "" if self.processed_image is None else " [Full res ready]"
            self.status_label.setText(f"✓ {self.params.image_type.value} ({mode}){sync_status}")
            
        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
            print(f"Processing error: {e}")
        finally:
            self.is_processing = False
    
    def display_image(self):
        """Display the processed image in the preview"""
        # Use proxy if available, otherwise full res
        display_source = self.processed_proxy if self.processed_proxy is not None else self.processed_image
        
        if display_source is None:
            return
        
        # Get label size
        label_width = self.image_label.width()
        label_height = self.image_label.height()
        
        # Convert numpy to PIL for resizing - ensure correct mode
        if len(display_source.shape) == 3:
            pil_image = Image.fromarray(display_source, mode='RGB')
        else:
            pil_image = Image.fromarray(display_source, mode='L')
        
        # Calculate aspect ratio
        img_width, img_height = pil_image.size
        aspect = img_width / img_height
        
        # Calculate display size
        if label_width / label_height > aspect:
            display_height = label_height - 20
            display_width = int(display_height * aspect)
        else:
            display_width = label_width - 20
            display_height = int(display_width / aspect)
        
        # Store scale for coordinate conversion
        self.display_scale = img_width / display_width
        
        # Resize with high quality
        display_pil = pil_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        
        # Convert to QPixmap - ensure correct color space
        if display_pil.mode == "RGB":
            data = display_pil.tobytes("raw", "RGB")
            qimage = QImage(data, display_width, display_height, display_width * 3, QImage.Format.Format_RGB888)
        else:
            # Grayscale
            data = display_pil.tobytes("raw", "L")
            qimage = QImage(data, display_width, display_height, display_width, QImage.Format.Format_Grayscale8)
        
        pixmap = QPixmap.fromImage(qimage)
        self.image_label.setPixmap(pixmap)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Run the advanced image editor"""
    app = QApplication(sys.argv)
    
    # Set style
    app.setStyle('Fusion')
    
    window = ImageEditorWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
