
import { ColorParams, FilmProfile } from './types';

// "Generic" Mask roughly based on Kodak Gold 200
export const DEFAULT_PARAMS: ColorParams = {
  // Mask (Brightest part of negative)
  mask_r: 0.80, 
  mask_g: 0.55,
  mask_b: 0.40,

  // Input WB
  input_temp: 0,
  input_tint: 0,

  // Tone
  exposure: -0.5,          // -0.5 EV (Slightly darker to prevent overexposure)
  brightness: 0.0,         // Midtone lift without affecting endpoints
  
  // Dynamics
  dynamic_compression: 0.0, // Defaults to deep expansion (handled in imageOps via -3.0 offset)
  dynamics_highlights: 0.0, // Reset to 0 (Disabled by default)
  dynamics_shadows: 0.0,    // Reset to 0 (Disabled by default)

  contrast: 1.0, 
  highlight_softness: 0.75,
  tone_smoothing: 0.2, // Default mild smoothing
  gamma: 1.0,
  black_point: 0.0, 
  white_point: 1.0,
  
  // Regional
  highlights: 0,
  shadows: 0,

  // Output WB
  output_temp: 0,
  output_tint: 0,
  wb_highlight_temp: 0,
  wb_highlight_tint: 0,
  wb_shadow_temp: 0,
  wb_shadow_tint: 0,

  // Grading (Split Toning)
  shadow_hue: 210, // Teal default
  shadow_sat: 0,
  highlight_hue: 35, // Orange default
  highlight_sat: 0,
  balance: 0,
  
  // Grading (Color EQ)
  sat_r: 1.0,
  sat_g: 1.0,
  sat_b: 1.0,

  // Color (Neutral)
  cyan_red: 0,
  magenta_green: 0,
  yellow_blue: 0,

  // Finishing
  saturation: 0.95, 
  vibrance: 0.15,
  sharpening: 0.00, 
};

export const FILM_PROFILES: FilmProfile[] = [
  {
    id: 'generic-color',
    name: 'Auto Color (Soft)',
    description: 'Balanced, dense shadows, highlight retention.',
    defaults: { ...DEFAULT_PARAMS }
  },
  {
    id: 'frontier-look',
    name: 'Frontier SP-3000',
    description: 'High contrast, punchy greens, glossy look.',
    defaults: {
      ...DEFAULT_PARAMS,
      contrast: 1.20,
      highlight_softness: 0.9,
      tone_smoothing: 0.1,
      saturation: 1.1,
      vibrance: 0.3,
      sharpening: 0.5, 
      magenta_green: 0.8, 
      cyan_red: -0.4,
      highlights: -0.3, 
    }
  },
  {
    id: 'cinematic',
    name: 'Cinematic / Log',
    description: 'Very flat, maximum dynamic range.',
    defaults: {
      ...DEFAULT_PARAMS,
      dynamic_compression: 3.0, // High compression (Log)
      exposure: 0.5, 
      contrast: 0.9,
      gamma: 0.95,
      saturation: 0.85,
      highlight_softness: 1.0,
      tone_smoothing: 0.4,
      black_point: 0.0, 
      shadows: 0.3, 
    }
  },
  {
    id: 'bw-contrast',
    name: 'B&W High Contrast',
    description: 'For black and white negatives.',
    defaults: {
      ...DEFAULT_PARAMS,
      mask_r: 0.9, mask_g: 0.9, mask_b: 0.9, 
      saturation: 0,
      vibrance: 0,
      contrast: 1.25,
      highlight_softness: 0.2,
      tone_smoothing: 0.0,
      dynamic_compression: -1.0,
    }
  }
];
