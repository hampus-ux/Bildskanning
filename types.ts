
export interface ColorParams {
  // --- CALIBRATION (THE NEGATIVE) ---
  // The color of the unexposed film base (linear 0-1).
  // We DIVIDE by this to neutralize the mask.
  mask_r: number;
  mask_g: number;
  mask_b: number;
  
  // --- INPUT CORRECTION (LIGHT SOURCE) ---
  // Applied BEFORE inversion to fix backlight variances
  input_temp: number;    // Blue-Amber axis
  input_tint: number;    // Green-Magenta axis

  // --- DENSITY (TONE) ---
  exposure: number;      // Overall brightness
  brightness: number;    // Midtone lift without affecting black/white points
  
  // ADVANCED DYNAMICS ENGINE
  dynamic_compression: number; // Main Log Curve
  dynamics_highlights: number; // Reinhard Tone Mapping for highlights
  dynamics_shadows: number;    // Power curve for shadow density

  contrast: number;      // S-Curve strength
  highlight_softness: number; // "Shoulder" - how gently whites roll off
  tone_smoothing: number; // New: Soft limiter to prevent histogram clipping
  gamma: number;         // Midtone density
  black_point: number;   // Shadow clipping
  white_point: number;   // Highlight clipping

  // --- REGIONAL TONE ---
  highlights: number;    // -1 to 1 (Recover vs Boost)
  shadows: number;       // -1 to 1 (Crush vs Lift)

  // --- WHITE BALANCE (OUTPUT) ---
  output_temp: number;   // Warmer/Cooler on positive (Global)
  output_tint: number;   // Magenta/Green on positive (Global)
  
  // ADVANCED WB
  wb_highlight_temp: number; // Warmth in highlights only (Golden Hour)
  wb_highlight_tint: number;
  wb_shadow_temp: number;    // Coolness in shadows only
  wb_shadow_tint: number;

  // --- GRADING (NEW) ---
  // Split Toning
  shadow_hue: number;    // 0-360
  shadow_sat: number;    // 0-100
  highlight_hue: number; // 0-360
  highlight_sat: number; // 0-100
  balance: number;       // -1 to 1

  // Color EQ (Channel Saturation)
  sat_r: number;         // 0-2
  sat_g: number;         // 0-2
  sat_b: number;         // 0-2

  // --- SCANNER COLOR (CMY) ---
  // Frontier/Noritsu style printer lights
  cyan_red: number;      // < 0 Cyan, > 0 Red
  magenta_green: number; // < 0 Magenta, > 0 Green
  yellow_blue: number;   // < 0 Yellow, > 0 Blue

  // --- FINISHING ---
  saturation: number;
  vibrance: number;      // Smart saturation (protects skin tones)
  sharpening: number;    // Edge enhancement
}

export interface FilmProfile {
  id: string;
  name: string;
  description: string;
  defaults: ColorParams;
}

export interface ProcessingStats {
  histogram: {
    r: number[];
    g: number[];
    b: number[];
  };
  min: { r: number; g: number; b: number };
  max: { r: number; g: number; b: number };
}

// --- MEDIA LIBRARY TYPES ---

export interface MediaRoll {
  id: string;
  name: string;
  fileCount: number;
  files: File[];
  status: 'pending' | 'imported';
}

export interface MediaOrder {
  id: string;
  name: string;
  rolls: MediaRoll[];
}
