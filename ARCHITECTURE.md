# Advanced Image Editor - Teknisk Arkitektur

## System Översikt

```
┌─────────────────────────────────────────────────────────────────┐
│                    ADVANCED IMAGE EDITOR                        │
│                   (advanced_image_editor.py)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
         ┌──────▼──────┐            ┌──────▼──────┐
         │  DATA MODEL │            │  UI LAYER   │
         └──────┬──────┘            └──────┬──────┘
                │                           │
    ┌───────────┴───────────┐              │
    │                       │              │
┌───▼────┐           ┌─────▼─────┐   ┌────▼────┐
│ Enums  │           │  Params   │   │ PyQt6   │
└────────┘           └───────────┘   │ Window  │
                                     └─────────┘
                          │
                ┌─────────┴─────────┐
                │                   │
         ┌──────▼──────┐     ┌─────▼─────┐
         │  PIPELINE   │     │  HELPERS  │
         │   CORE      │     └───────────┘
         └─────────────┘
```

## Modul Breakdown

### 1. Enums (Lines ~27-47)
```python
ImageType       # Color Negative, B&W Negative, Positive
FilmProfile     # Kodak/Fuji emulation profiles  
ToneCurveProfile # Final curve styles
```

### 2. AutoEditParams (Lines ~50-181)
Dataclass med **30+ parametrar** grupperade i 9 steg:
- Histogram centering (3 params)
- Black/white point (6 params)
- Midtone correction (4 params)
- Dynamic range (3 params)
- Color balance (3 params)
- Smoothing (5 params)
- Saturation (3 params)
- Protection (2 params)
- Final curve (2 params)

**Tre fabriksmetoder:**
```python
AutoEditParams.for_color_negative()   # Optimized for color film
AutoEditParams.for_bw_negative()      # Optimized for B&W film
AutoEditParams.for_positive()         # Optimized for positive images
```

### 3. Pipeline Core (Lines ~187-380)

#### Main Pipeline Function:
```python
apply_edit_pipeline(image: np.ndarray, params: AutoEditParams) -> np.ndarray
```

**Flow:**
```
Input (uint8) 
    → float32 [0,1]
    → Negative Inversion (if needed)
    → 9 Processing Steps
    → Clip & Convert
    → Output (uint8)
```

#### Processing Steps (in order):
1. `_invert_color_negative()` / `_invert_bw_negative()`
2. `_histogram_centering()`
3. `_apply_bw_point()`
4. `_apply_midtone_correction()`
5. `_apply_dynamic_range()`
6. `_apply_color_balance()`
7. `_apply_smoothing()`
8. `_apply_saturation()`
9. `_apply_protection()`
10. `_apply_final_curve()`

### 4. PyQt6 UI (Lines ~387-670)

#### Main Window Class:
```python
ImageEditorWindow(QMainWindow)
```

**Components:**
- Left Panel: File controls + Image preview (600x400+ px)
- Right Panel: Scrollable control panel with 9 group boxes
- Status Bar: Current status and file info

#### Control Creators:
```python
create_histogram_controls()      # Step 1
create_bw_point_controls()       # Step 2
create_midtone_controls()        # Step 3
create_dynamic_range_controls()  # Step 4
create_color_balance_controls()  # Step 5
create_smoothing_controls()      # Step 6
create_saturation_controls()     # Step 7
create_protection_controls()     # Step 8
create_final_curve_controls()    # Step 9
```

Each returns a `QGroupBox` with:
- Checkable (enable/disable step)
- Sliders for numeric params
- Combo boxes for enums
- Real-time update on change

## Data Flow

```
User Action (UI)
    ↓
update_param(name, value)
    ↓
params.{name} = value
    ↓
process_image()
    ↓
apply_edit_pipeline(original_image, params)
    ↓
[Pipeline Processing - 9 steps]
    ↓
processed_image (numpy array)
    ↓
display_image()
    ↓
Convert to QPixmap
    ↓
Update QLabel
    ↓
User sees result
```

## Image Type Logic

```python
on_image_type_changed(text):
    if "Color Negative":
        params = AutoEditParams.for_color_negative()
        Enable: color_balance, saturation
        
    elif "B&W Negative":
        params = AutoEditParams.for_bw_negative()
        Disable: color_balance, saturation
        Enable: smoothing
        
    elif "Positive":
        params = AutoEditParams.for_positive()
        Enable: all (with lower defaults)
    
    update_ui_from_params()
    process_image()
```

## Pipeline Step Details

### Step 1: Histogram Centering
```python
Method: mean or median
Effect: Shifts entire histogram to target midpoint
Use case: Correct under/over-exposure before processing
```

### Step 2: Black & White Point
```python
Method: Percentile-based scaling
Effect: Stretches dynamic range, sets pure black/white
Use case: Maximize contrast, remove film fog
```

### Step 3: Midtone Correction
```python
Method: Gamma curve (power function)
Effect: Brightens/darkens midtones without touching endpoints
Use case: Fine-tune overall brightness perception
```

### Step 4: Dynamic Range Expansion
```python
Method: Parametric toe and shoulder curves
Effect: Film-like rolloff in shadows and highlights
Use case: Emulate film look, prevent harsh clipping
```

### Step 5: Color Balance
```python
Method: Per-channel normalization + film profile shifts
Effect: Neutralizes color casts, applies film characteristics
Use case: Remove orange mask, emulate film stocks
```

### Step 6: Local Contrast Smoothing
```python
Method: Bilateral filter (edge-preserving blur)
Effect: Reduces grain/noise while keeping edges sharp
Use case: Clean up scan artifacts, reduce film grain
Performance: SLOW on large images (disable if needed)
```

### Step 7: Saturation Adjustment
```python
Method: HSV conversion + density-modulated saturation
Effect: Natural-looking saturation that varies with luminosity
Use case: Emulate how film saturation varies with exposure
```

### Step 8: Highlight & Shadow Protection
```python
Method: Masking + compression/lift
Effect: Prevents clipping, recovers detail at extremes
Use case: Rescue overexposed highlights, lift blocked shadows
```

### Step 9: Final Tone Curve
```python
Method: Parametric curves or lookup tables
Profiles:
  - Neutral: Linear (no change)
  - Frontier: Fuji scanner style (lifted shadows)
  - Noritsu: Noritsu scanner style (compressed highlights)
  - Portra-like: Smooth S-curve with soft rolloff
  - Soft: Low contrast, lifted blacks
```

## Performance Considerations

### Fast Operations (< 100ms on typical image):
- Histogram centering
- B&W point scaling
- Gamma correction
- Color balance
- Saturation adjustment
- Protection
- Final curves

### Slow Operations (> 500ms on large images):
- **Local Contrast Smoothing** (bilateral filter)
  - O(n × kernel_size²) complexity
  - Can take 1-3 seconds on 24MP images
  - Consider disabling for real-time editing

### Optimization Tips:
1. Process on downscaled preview (not implemented yet)
2. Cache intermediate results (not implemented yet)
3. Use GPU acceleration via CUDA (future enhancement)
4. Parallel processing for batch operations (future)

## Dependencies

```
Pillow (PIL)    → Image I/O
NumPy           → Array operations
OpenCV (cv2)    → Advanced processing (bilateral, HSV)
PyQt6           → GUI framework
```

## File Format Support

**Input:**
- JPEG, PNG, TIFF, BMP, WebP
- RGB or grayscale
- Any bit depth (converted to 8-bit internally)

**Output:**
- JPEG (lossy, good for web)
- PNG (lossless, large files)
- TIFF (lossless, archival quality)

## Memory Usage

For a 24MP image (6000×4000):
```
Original (uint8):     6000 × 4000 × 3 = 72 MB
Pipeline (float32):   6000 × 4000 × 3 × 4 = 288 MB
Peak usage:          ~400-500 MB (with intermediate buffers)
```

## Thread Safety

Current implementation: **Single-threaded**
- All processing on main thread
- UI updates synchronously
- No race conditions

Future: Multi-threading for batch processing

## Extension Points

### Add New Pipeline Step:
1. Add enable flag to `AutoEditParams`
2. Add parameters for the step
3. Create `_apply_new_step()` function
4. Insert in `apply_edit_pipeline()` at desired position
5. Create UI controls with `create_new_step_controls()`
6. Add to control panel in `create_control_panel()`

### Add New Film Profile:
1. Add entry to `FilmProfile` enum
2. Add case in `_apply_color_balance()` with RGB multipliers
3. Profile appears automatically in UI dropdown

### Add New Tone Curve:
1. Add entry to `ToneCurveProfile` enum
2. Create curve function in `_apply_final_curve()`
3. Add to curve_map dictionary
4. Appears automatically in UI

## Code Style

- **Type hints**: All functions have type annotations
- **Docstrings**: All public functions documented
- **NumPy style**: Vectorized operations, no loops
- **Functional**: Pure functions for pipeline steps
- **Object-oriented**: PyQt6 UI as class hierarchy

## Testing

Run pipeline tests:
```bash
python test_pipeline.py
```

Expected output:
```
✅ All pipeline tests completed successfully!
```

---

**Last Updated**: 2025-11-25
