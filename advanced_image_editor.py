#!/usr/bin/env python3
"""
Advanced Image Editor Module
Supports Color Negatives, B&W Negatives, and Positive Images
with professional-grade editing pipeline
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple
import numpy as np
from PIL import Image
import cv2

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QPushButton, QComboBox, QGroupBox, QScrollArea,
    QFileDialog, QMessageBox, QCheckBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
import sys


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
    """Center histogram around target midpoint"""
    if params.mid_detection_method == "mean":
        current_mid = np.mean(img)
    else:  # median
        current_mid = np.median(img)
    
    # Shift to target
    shift = params.target_midpoint - current_mid
    img = img + shift
    
    return np.clip(img, 0, 1)


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
    
    # Neutral gray balance
    if params.neutral_balance_strength > 0:
        # Find gray point (areas that should be neutral)
        gray_target = np.median(img, axis=(0, 1))
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
    """Apply local contrast smoothing with edge preservation"""
    if params.smoothing_strength == 0:
        return img
    
    # Convert to uint8 for OpenCV
    img_uint8 = (img * 255).astype(np.uint8)
    
    # Calculate kernel size based on image size
    h, w = img.shape[:2]
    kernel_size = max(5, int(min(h, w) * 0.01))
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    # Apply bilateral filter (edge-preserving smoothing)
    if len(img.shape) == 3:
        smoothed = cv2.bilateralFilter(
            img_uint8,
            d=kernel_size,
            sigmaColor=75 * params.preserve_edges,
            sigmaSpace=75 * params.smoothing_strength
        )
    else:
        smoothed = cv2.bilateralFilter(
            img_uint8,
            d=kernel_size,
            sigmaColor=75 * params.preserve_edges,
            sigmaSpace=75 * params.smoothing_strength
        )
    
    smoothed = smoothed.astype(np.float32) / 255.0
    
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
    """Apply density-modulated saturation adjustment"""
    if len(img.shape) != 3 or img.shape[2] != 3:
        return img
    
    # Convert to HSV
    img_uint8 = (img * 255).astype(np.uint8)
    hsv = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2HSV).astype(np.float32)
    
    # Calculate density (luminosity)
    luminosity = img[:, :, 0] * 0.299 + img[:, :, 1] * 0.587 + img[:, :, 2] * 0.114
    
    # Modulate saturation by density (film characteristic)
    # Denser areas (darker in negative, lighter in positive) get more saturation
    density_factor = 1.0 + params.density_modulation_strength * (luminosity - 0.5)
    
    # Boost shadow colors
    shadow_boost = np.clip(1 - luminosity, 0, 1) * params.shadow_color_boost
    density_factor += shadow_boost
    
    # Apply base saturation with density modulation
    hsv[:, :, 1] *= params.base_saturation * density_factor
    hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
    
    # Convert back
    result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
    
    return result.astype(np.float32) / 255.0


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
# PYQT6 USER INTERFACE
# ============================================================================

class ImageEditorWindow(QMainWindow):
    """Main window for the advanced image editor"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Image Editor - DSLR Scan Processing")
        self.setGeometry(100, 100, 1400, 900)
        
        # Image data
        self.original_image: Optional[np.ndarray] = None
        self.processed_image: Optional[np.ndarray] = None
        self.current_file_path: Optional[str] = None
        
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
        
        # Image preview
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(600, 400)
        self.image_label.setStyleSheet("border: 2px solid #ccc; background-color: #2b2b2b;")
        self.image_label.setScaledContents(False)
        left_panel.addWidget(self.image_label, stretch=1)
        
        # Status
        self.status_label = QLabel("Load an image to start")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        left_panel.addWidget(self.status_label)
        
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
    
    def load_image(self):
        """Load an image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Image",
            "",
            "Image Files (*.jpg *.jpeg *.png *.tif *.tiff *.bmp);;All Files (*.*)"
        )
        
        if file_path:
            try:
                # Load with PIL and convert to numpy
                pil_image = Image.open(file_path)
                
                # Convert to RGB if needed
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                self.original_image = np.array(pil_image)
                self.current_file_path = file_path
                
                self.status_label.setText(f"Loaded: {file_path}")
                self.process_image()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
    
    def save_image(self):
        """Save the processed image"""
        if self.processed_image is None:
            QMessageBox.warning(self, "Warning", "No image to save!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "",
            "JPEG (*.jpg);;PNG (*.png);;TIFF (*.tif);;All Files (*.*)"
        )
        
        if file_path:
            try:
                # Convert numpy to PIL and save
                pil_image = Image.fromarray(self.processed_image)
                pil_image.save(file_path)
                self.status_label.setText(f"Saved: {file_path}")
                QMessageBox.information(self, "Success", "Image saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save image: {str(e)}")
    
    def process_image(self):
        """Process the image with current parameters"""
        if self.original_image is None:
            return
        
        try:
            # Apply pipeline
            self.processed_image = apply_edit_pipeline(self.original_image, self.params)
            
            # Display
            self.display_image()
            
            self.status_label.setText(f"Processing complete - {self.params.image_type.value}")
            
        except Exception as e:
            QMessageBox.critical(self, "Processing Error", f"Error processing image: {str(e)}")
    
    def display_image(self):
        """Display the processed image in the preview"""
        if self.processed_image is None:
            return
        
        # Get label size
        label_width = self.image_label.width()
        label_height = self.image_label.height()
        
        # Convert numpy to PIL for resizing
        pil_image = Image.fromarray(self.processed_image)
        
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
        
        # Resize
        display_pil = pil_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        
        # Convert to QPixmap
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
