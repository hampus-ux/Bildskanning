import React, { useState, useRef, useEffect } from 'react';
import { Upload, Download, Wand2, Image as ImageIcon, SlidersHorizontal, Palette, RefreshCw, Eye, Droplet, Pipette, Film, Check, RotateCcw, X, Layers, Crop as CropIcon, RotateCw, RotateCcw as RotateLeft, FolderOpen, Database, ChevronDown, ChevronRight, Play, Copy, Clipboard } from 'lucide-react';
import { DEFAULT_PARAMS, FILM_PROFILES } from './constants';
import { ColorParams, ProcessingStats, MediaOrder, MediaRoll } from './types';
import { processImage, analyzeNegative, generateThumbnail, rotateImage, transformImage } from './services/imageOps';
import { Slider } from './components/Slider';
import { Histogram } from './components/Histogram';
import { processedImageCache } from './services/imageCache';

// Declare UTIF & JSZip
declare global {
  interface Window {
    UTIF: any;
    JSZip: any;
    electronAPI?: {
            openDirectoryDialog: () => Promise<string | null>;
            createDirectory: (dirPath: string) => Promise<{ ok: boolean; error?: string }>;
            saveBytes: (filePath: string, bytes: ArrayBuffer) => Promise<{ ok: boolean; error?: string }>;
    };
  }
}

interface BatchItem {
    id: string;
    file: File;
    imageData: ImageData;
    thumbnail: string;
    name: string;
    params: ColorParams;
    rotation: number; // Track cumulative rotation in degrees
    stats?: ProcessingStats; // Store histogram data per image
}

const getImageWithRotation = (image: ImageData, rotation: number = 0) => {
    if (!rotation) return image;
    return rotateImage(image, rotation);
};

const App: React.FC = () => {
  // --- VIEW STATE ---
  const [viewMode, setViewMode] = useState<'library' | 'develop'>('develop');

  // --- PERFORMANCE STATE ---

  // --- MEDIA LIBRARY STATE ---
  const [mediaLibrary, setMediaLibrary] = useState<MediaOrder[]>([]);
  const [expandedOrders, setExpandedOrders] = useState<Set<string>>(new Set());
  const folderInputRef = useRef<HTMLInputElement>(null);

  // --- BATCH / EDIT STATE ---
  const [batchItems, setBatchItems] = useState<BatchItem[]>([]);
  const [activeItemId, setActiveItemId] = useState<string | null>(null);
  
  // Current View State
  const [originalImage, setOriginalImage] = useState<ImageData | null>(null);
  const [processedImage, setProcessedImage] = useState<ImageData | null>(null);
  const [flatfieldImage, setFlatfieldImage] = useState<ImageData | null>(null);
  
  // Active Params
  const [params, setParams] = useState<ColorParams>(DEFAULT_PARAMS);
  
  const [stats, setStats] = useState<ProcessingStats | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showOriginal, setShowOriginal] = useState(false);
  const [isPickingWB, setIsPickingWB] = useState(false);
  
  // Editing Modes
  const [editHistory, setEditHistory] = useState<ImageData[]>([]);

  // Transform Mode
  const [transformMode, setTransformMode] = useState(false);
  const [straightenAngle, setStraightenAngle] = useState(0);
  const [cropRect, setCropRect] = useState({ x: 0.05, y: 0.05, w: 0.9, h: 0.9 });
  const [isDraggingCrop, setIsDraggingCrop] = useState<'move' | 'tl' | 'tr' | 'bl' | 'br' | null>(null);
  const [savedCrop, setSavedCrop] = useState<{ angle: number; rect: { x: number; y: number; w: number; h: number } } | null>(null);

  const [analysisPadding, setAnalysisPadding] = useState<number>(0.05);
  
  const [activeTab, setActiveTab] = useState<'basic' | 'calibration'>('basic');
  const [selectedProfileId, setSelectedProfileId] = useState<string>(FILM_PROFILES[0].id);

  // Copy/Paste State
  const [copiedParams, setCopiedParams] = useState<ColorParams | null>(null);

  // Processed Images Tracking
  const [processedImageIds, setProcessedImageIds] = useState<Set<string>>(new Set());

  // Export State
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportName, setExportName] = useState('');
  const [exportSuffix, setExportSuffix] = useState('_converted');
  const [exportFormats, setExportFormats] = useState<Set<'jpeg' | 'tiff'>>(new Set(['jpeg']));
  const [exportQuality, setExportQuality] = useState(0.95);
  const [exportFolderName, setExportFolderName] = useState('Converted');
  const [exportDirectory, setExportDirectory] = useState('');

  // Refs
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const flatfieldInputRef = useRef<HTMLInputElement>(null);
  const overlayRef = useRef<HTMLDivElement>(null);

  // --- UTILS ---
  const ensureUTIF = async () => {
    if (window.UTIF && typeof window.UTIF.decode === 'function') return true;
    
    console.log("UTIF not found, attempting dynamic load...");
    return new Promise<boolean>((resolve) => {
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/utif@2.0.1/UTIF.js';
        script.async = true;
        script.onload = () => {
            console.log("UTIF loaded dynamically");
            resolve(true);
        };
        script.onerror = () => {
            console.error("Failed to load UTIF");
            resolve(false);
        };
        document.body.appendChild(script);
    });
  };

  const ensureJSZip = async () => {
      if (window.JSZip) return true;
      return new Promise<boolean>((resolve) => {
          const script = document.createElement('script');
          script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
          script.async = true;
          script.onload = () => resolve(true);
          script.onerror = () => resolve(false);
          document.body.appendChild(script);
      });
  }

  const loadImageFile = async (file: File): Promise<ImageData> => {
    const fileName = file.name.toLowerCase();
    const isTiff = fileName.endsWith('.tif') || fileName.endsWith('.tiff');
    // Check for common RAW formats
    const isRaw = fileName.endsWith('.dng') || isTiff || fileName.endsWith('.arw') || fileName.endsWith('.cr2') || fileName.endsWith('.nef');

    if (isRaw) {
       const loaded = await ensureUTIF();
       if (!loaded) throw new Error("Could not load RAW decoder library.");
       
       return new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = async (event) => {
             if (!event.target?.result) return reject("Read failure");
             try {
                 const buffer = event.target.result as ArrayBuffer;
                 let ifds: any[] = [];
                 try {
                    ifds = window.UTIF.decode(buffer);
                 } catch (e) {
                    console.warn("UTIF decode structure failed", e);
                 }
                 
                 const candidates: any[] = [];
                 const collectIFDs = (list: any[]) => {
                     if(!list) return;
                     for (const ifd of list) {
                         candidates.push(ifd);
                         if (ifd.subIFD) collectIFDs(ifd.subIFD);
                     }
                 };
                 collectIFDs(ifds);

                 candidates.sort((a, b) => (b.width * b.height) - (a.width * a.height));

                 let decodedImageData: ImageData | null = null;

                 for (const ifd of candidates) {
                     try {
                         window.UTIF.decodeImage(buffer, ifd);
                         const rgba = window.UTIF.toRGBA8(ifd);
                         if (rgba && ifd.width > 0 && ifd.height > 0) {
                             decodedImageData = new ImageData(new Uint8ClampedArray(rgba), ifd.width, ifd.height);
                             break; 
                         }
                     } catch (err) {
                         // console.warn("UTIF decodeImage failed for IFD", err);
                     }

                     try {
                         let offset = 0;
                         let length = 0;

                         if (ifd.t513 && ifd.t513[0]) {
                             offset = ifd.t513[0];
                             length = ifd.t514 ? ifd.t514[0] : 0;
                         } else if (ifd.t273 && ifd.t273[0]) {
                             offset = ifd.t273[0];
                             length = ifd.t279 ? ifd.t279[0] : 0;
                         }

                         if (offset > 0 && length > 0 && (offset + length) <= buffer.byteLength) {
                             const view = new DataView(buffer);
                             if (view.getUint8(offset) === 0xFF && view.getUint8(offset + 1) === 0xD8) {
                                 const blob = new Blob([new Uint8Array(buffer, offset, length)], { type: 'image/jpeg' });
                                 const img = await new Promise<HTMLImageElement>((resImg, rejImg) => {
                                     const i = new Image();
                                     i.onload = () => resImg(i);
                                     i.onerror = rejImg;
                                     i.src = URL.createObjectURL(blob);
                                 });

                                 const cvs = document.createElement('canvas');
                                 cvs.width = img.width;
                                 cvs.height = img.height;
                                 const ctx = cvs.getContext('2d');
                                 if (ctx) {
                                     ctx.drawImage(img, 0, 0);
                                     decodedImageData = ctx.getImageData(0, 0, img.width, img.height);
                                     break; 
                                 }
                             }
                         }
                     } catch (err) {
                         // console.warn("JPEG extraction failed", err);
                     }
                 }

                 if (decodedImageData) {
                     resolve(decodedImageData);
                 } else {
                     if (isTiff) {
                         const blob = new Blob([buffer], { type: 'image/tiff' });
                         const url = URL.createObjectURL(blob);
                         const img = new Image();
                         img.onload = () => {
                             const cvs = document.createElement('canvas');
                             cvs.width = img.width;
                             cvs.height = img.height;
                             const ctx = cvs.getContext('2d');
                             if (ctx) {
                                 ctx.drawImage(img, 0, 0);
                                 URL.revokeObjectURL(url);
                                 resolve(ctx.getImageData(0, 0, img.width, img.height));
                             } else {
                                 URL.revokeObjectURL(url);
                                 reject("Canvas init failed");
                             }
                         };
                         img.onerror = () => {
                             URL.revokeObjectURL(url);
                             reject("Browser could not decode TIFF.");
                         };
                         img.src = url;
                     } else {
                         reject("Could not decode any image frames from RAW file. The format might be unsupported or compressed.");
                     }
                 }
             } catch (err) { reject(err); }
          };
          reader.readAsArrayBuffer(file);
       });
    } else {
       return new Promise((resolve, reject) => {
           const reader = new FileReader();
           reader.onload = (event) => {
               const img = new Image();
               img.onload = () => {
                   const cvs = document.createElement('canvas');
                   cvs.width = img.width;
                   cvs.height = img.height;
                   const ctx = cvs.getContext('2d');
                   if (ctx) {
                       ctx.drawImage(img, 0, 0);
                       resolve(ctx.getImageData(0, 0, img.width, img.height));
                   } else reject("Canvas init failed");
               };
               img.onerror = () => reject("Image load failed");
               img.src = event.target?.result as string;
           };
           reader.readAsDataURL(file);
       });
    }
  };

  const resizeForWork = (rawData: ImageData): ImageData => {
      const maxDim = 2500; 
      if (rawData.width <= maxDim && rawData.height <= maxDim) return rawData;
      
      const ratio = Math.min(maxDim / rawData.width, maxDim / rawData.height);
      const w = Math.round(rawData.width * ratio);
      const h = Math.round(rawData.height * ratio);
      
      const cvs = document.createElement('canvas');
      cvs.width = w;
      cvs.height = h;
      const ctx = cvs.getContext('2d');
      if (!ctx) return rawData;
      
      const tempCvs = document.createElement('canvas');
      tempCvs.width = rawData.width;
      tempCvs.height = rawData.height;
      const tempCtx = tempCvs.getContext('2d');
      if (tempCtx) {
          tempCtx.putImageData(rawData, 0, 0);
          ctx.drawImage(tempCvs, 0, 0, w, h);
          return ctx.getImageData(0, 0, w, h);
      }
      return rawData;
  }

    // --- CACHE LIFECYCLE ---
    useEffect(() => {
        return () => {
            processedImageCache.clear();
        };
    }, []);

  // --- MEDIA LIBRARY LOGIC ---

  const handleFolderSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const tempLibrary: Record<string, { name: string; rolls: Record<string, File[]> }> = {};

    // EXPLICITLY CAST FILE TO 'File' TO FIX BUILD ERROR
    Array.from(files).forEach((file: File) => {
      // Check for image extension
      if (!file.name.match(/\.(jpg|jpeg|png|tif|tiff|dng|arw|cr2|nef)$/i)) return;
      
      // Parse Path: Order / Roll / File
      const pathParts = file.webkitRelativePath.split('/');
      
      // Need at least Order/Roll/File or Root/Order/Roll/File
      // Let's assume the user selected a "Root" folder containing Orders.
      // Root -> Order -> Roll -> File
      if (pathParts.length < 3) return;

      // We usually want the parent of the file to be the Roll, and the parent of that to be the Order.
      const rollName = pathParts[pathParts.length - 2];
      const orderName = pathParts[pathParts.length - 3];

      if (!tempLibrary[orderName]) {
        tempLibrary[orderName] = { name: orderName, rolls: {} };
      }
      if (!tempLibrary[orderName].rolls[rollName]) {
        tempLibrary[orderName].rolls[rollName] = [];
      }
      tempLibrary[orderName].rolls[rollName].push(file);
    });

    // Convert to Array
    const orders: MediaOrder[] = Object.values(tempLibrary).map(order => ({
      id: order.name,
      name: order.name,
      rolls: Object.entries(order.rolls).map(([rName, rFiles]) => ({
        id: `${order.name}-${rName}`,
        name: rName,
        fileCount: rFiles.length,
        files: rFiles,
        status: 'pending'
      }))
    }));

    setMediaLibrary(orders);
    // Expand all orders by default if there are few
    if (orders.length < 5) {
      setExpandedOrders(new Set(orders.map(o => o.id)));
    }
  };

  const toggleOrderExpand = (orderId: string) => {
    const next = new Set(expandedOrders);
    if (next.has(orderId)) next.delete(orderId);
    else next.add(orderId);
    setExpandedOrders(next);
  };

  const loadRollToEditor = async (roll: MediaRoll) => {
    if (roll.files.length === 0) return;
    setIsProcessing(true);
    
    // Clear current batch
    setBatchItems([]);
    setOriginalImage(null);
    setProcessedImage(null);
    setActiveItemId(null);

    const newBatchItems: BatchItem[] = [];
    try {
        for (const file of roll.files) {
            try {
                const data = await loadImageFile(file);
                const resized = resizeForWork(data);
                const thumb = generateThumbnail(resized);
                newBatchItems.push({
                    id: Math.random().toString(36).substr(2, 9),
                    file: file,
                    imageData: resized,
                    thumbnail: thumb,
                    name: file.name,
                    params: { ...DEFAULT_PARAMS },
                    rotation: 0
                });
            } catch (err: any) {
                console.error(`Failed to load ${file.name}`, err);
            }
        }
        if (newBatchItems.length > 0) {
            setBatchItems(newBatchItems);
            // Select first image without auto-analysis
            selectBatchItem(newBatchItems[0]);
            
            // Switch View
            setViewMode('develop');
        }
    } catch (e: any) {
        alert("Batch load error: " + e.message);
    } finally {
        setIsProcessing(false);
    }
  };

  // --- EXISTING UPLOAD LOGIC (Single/Multi File) ---
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []) as File[];
    if (files.length === 0) return;
    setIsProcessing(true);
    const newBatchItems: BatchItem[] = [];
    try {
        for (const file of files) {
            try {
                const data = await loadImageFile(file);
                const resized = resizeForWork(data);
                const thumb = generateThumbnail(resized);
                newBatchItems.push({
                    id: Math.random().toString(36).substr(2, 9),
                    file: file,
                    imageData: resized,
                    thumbnail: thumb,
                    name: file.name,
                    params: { ...DEFAULT_PARAMS },
                    rotation: 0
                });
            } catch (err: any) {
                console.error(`Failed to load ${file.name}`, err);
                alert(`Error loading ${file.name}: ${err.message || err}`);
            }
        }
        if (newBatchItems.length > 0) {
            setBatchItems(prev => [...prev, ...newBatchItems]);
            if (!activeItemId) {
                selectBatchItem(newBatchItems[0]);
            }
            setViewMode('develop');
        }
    } catch (e: any) {
        alert("Batch load error: " + e.message);
    } finally {
        setIsProcessing(false);
        if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const selectBatchItem = (item: BatchItem) => {
      setActiveItemId(item.id);
      setOriginalImage(item.imageData);
      setParams(item.params);
      // Restore stats for this image if available
      if (item.stats) {
        setStats(item.stats);
      }
      setEditHistory([]);
      setTransformMode(false); 
  };

  const removeBatchItem = (itemId: string) => {
      setBatchItems(prev => {
          const filtered = prev.filter(item => item.id !== itemId);
          // If we deleted the active item, select the first remaining one
          if (activeItemId === itemId && filtered.length > 0) {
              const firstItem = filtered[0];
              setActiveItemId(firstItem.id);
              setOriginalImage(firstItem.imageData);
              setParams(firstItem.params);
              // Restore stats for the newly selected image
              if (firstItem.stats) {
                setStats(firstItem.stats);
              }
              setEditHistory([]);
          } else if (filtered.length === 0) {
              // No items left
              setActiveItemId(null);
              setOriginalImage(null);
              setProcessedImage(null);
              setParams(DEFAULT_PARAMS);
          }
          return filtered;
      });
  };

  useEffect(() => {
      if (!activeItemId) return;
      setBatchItems(prev => prev.map(item => 
          item.id === activeItemId ? { ...item, params: params } : item
      ));
  }, [params, activeItemId]);

  const openExportModal = () => {
      if (batchItems.length === 0) return;
      if (batchItems.length === 1) {
          const item = batchItems[0];
          const name = item.name.replace(/\.[^/.]+$/, "");
          setExportName(name + "_converted");
      } else {
          setExportSuffix("_converted");
      }
      setShowExportModal(true);
  };

    const performExport = async () => {
      setShowExportModal(false);
      setIsProcessing(true);

      if (exportFormats.size === 0) {
          alert("Please select at least one format to export.");
          setIsProcessing(false);
          return;
      }

      // Helper function to encode TIFF
      const encodeTIFF = async (imageData: ImageData): Promise<Blob | null> => {
          const loaded = await ensureUTIF();
          if (!loaded) {
              console.error("UTIF library not available for TIFF export");
              return null;
          }

          const { width, height, data } = imageData;
          const rgba = new Uint8Array(data);
          
          // Create IFD (Image File Directory) for TIFF
          const ifd = {
              t256: [width],           // ImageWidth
              t257: [height],          // ImageLength
              t258: [8, 8, 8, 8],      // BitsPerSample (RGBA)
              t259: [1],               // Compression (none)
              t262: [2],               // PhotometricInterpretation (RGB)
              t273: [1000],            // StripOffsets (placeholder)
              t277: [4],               // SamplesPerPixel (RGBA)
              t278: [height],          // RowsPerStrip
              t279: [width * height * 4], // StripByteCounts
              t282: [72],              // XResolution
              t283: [72],              // YResolution
              t284: [1],               // PlanarConfiguration
              t296: [2],               // ResolutionUnit (inches)
              t338: [1]                // ExtraSamples (associated alpha)
          };

          try {
              const tiffBuffer = window.UTIF.encode([rgba.buffer], [ifd]);
              return new Blob([tiffBuffer], { type: 'image/tiff' });
          } catch (e) {
              console.error("TIFF encoding error:", e);
              return null;
          }
      };

            const useDirectFS = !!exportDirectory && window.electronAPI && typeof window.electronAPI.createDirectory === 'function' && typeof window.electronAPI.saveBytes === 'function';

            // Helper to save a blob via Electron
            const saveBlobToPath = async (folderPath: string, baseName: string, ext: string, blob: Blob) => {
                const resDir = await window.electronAPI!.createDirectory(folderPath);
                if (!resDir || resDir.ok === false) throw new Error(resDir?.error || 'Failed to create directory');
                const bytes = await blob.arrayBuffer();
                const filePath = `${folderPath}\\${baseName}.${ext}`;
                const resSave = await window.electronAPI!.saveBytes(filePath, bytes);
                if (!resSave || resSave.ok === false) throw new Error(resSave?.error || 'Failed to save file');
            };

              if (batchItems.length === 1) {
          // Single image export
          const item = batchItems[0];
          const sourceImage = getImageWithRotation(item.imageData, item.rotation || 0);
          const result = processImage(sourceImage, item.params, flatfieldImage).output;
          
          const cvs = document.createElement('canvas');
          cvs.width = result.width;
          cvs.height = result.height;
          const ctx = cvs.getContext('2d');
          if (!ctx) {
              setIsProcessing(false);
              return;
          }
          ctx.putImageData(result, 0, 0);

                    // Determine base filename
                    const originalBase = item.name.replace(/\.[^/.]+$/, "");
                    const baseForSave = exportName && exportName.trim().length > 0 
                        ? exportName.trim() 
                        : `${originalBase}${exportSuffix}`;

                    // Export each selected format
                    for (const format of Array.from(exportFormats)) {
                            let blob: Blob | null = null;
                            let ext = '';

                            if (format === 'jpeg') {
                                    blob = await new Promise<Blob | null>(resolve => cvs.toBlob(resolve, 'image/jpeg', exportQuality));
                                    ext = 'jpg';
                            } else if (format === 'tiff') {
                                    blob = await encodeTIFF(result);
                                    ext = 'tif';
                            }

                            if (!blob) continue;

                              if (useDirectFS) {
                                    const mainFolder = `${exportDirectory}\\${exportFolderName}`;
                                    const subFolder = `${mainFolder}\\${format === 'jpeg' ? 'JPEG' : 'TIFF'}`;
                                  await saveBlobToPath(subFolder, baseForSave, ext, blob);
                            } else {
                                    const url = URL.createObjectURL(blob);
                                    const a = document.createElement('a');
                                    a.href = url;
                                  a.download = `${baseForSave}.${ext}`;
                                    document.body.appendChild(a);
                                    a.click();
                                    document.body.removeChild(a);
                                    URL.revokeObjectURL(url);
                            }
                    }
      } else {
                    // Batch export
                    const batchSize = 4;
                    const mainFolder = useDirectFS ? `${exportDirectory}\\${exportFolderName}` : null;
                    const subFolders: Record<'jpeg'|'tiff', string> = {
                        jpeg: mainFolder ? `${mainFolder}\\JPEG` : '',
                        tiff: mainFolder ? `${mainFolder}\\TIFF` : ''
                    };

                    if (useDirectFS) {
                        await window.electronAPI!.createDirectory(mainFolder!);
                        if (exportFormats.has('jpeg')) await window.electronAPI!.createDirectory(subFolders.jpeg);
                        if (exportFormats.has('tiff')) await window.electronAPI!.createDirectory(subFolders.tiff);
                    } else {
                        // Fallback to ZIP
                        const loaded = await ensureJSZip();
                        if (!loaded) {
                            alert('Could not load zipping library.');
                            setIsProcessing(false);
                            return;
                        }
                    }

                    const zip = useDirectFS ? null : new window.JSZip();
                    const mainZipFolder = useDirectFS ? null : zip.folder(exportFolderName);
                    const zipFolders: Record<string, any> = {};
                    if (!useDirectFS) {
                        if (exportFormats.has('jpeg')) zipFolders['jpeg'] = mainZipFolder.folder('JPEG');
                        if (exportFormats.has('tiff')) zipFolders['tiff'] = mainZipFolder.folder('TIFF');
                    }

                    for (let i = 0; i < batchItems.length; i += batchSize) {
                        const batch = batchItems.slice(i, i + batchSize);
                        await Promise.all(batch.map(async (item) => {
                            const sourceImage = getImageWithRotation(item.imageData, item.rotation || 0);
                            const result = processImage(sourceImage, item.params, flatfieldImage).output;

                            const cvs = document.createElement('canvas');
                            cvs.width = result.width;
                            cvs.height = result.height;
                            const ctx = cvs.getContext('2d');
                            if (!ctx) return;
                            ctx.putImageData(result, 0, 0);
                            const baseName = item.name.replace(/\.[^/.]+$/, "");

                            for (const format of Array.from(exportFormats)) {
                                let blob: Blob | null = null;
                                let ext = '';
                                if (format === 'jpeg') {
                                    blob = await new Promise<Blob | null>(resolve => cvs.toBlob(resolve, 'image/jpeg', exportQuality));
                                    ext = 'jpg';
                                } else if (format === 'tiff') {
                                    blob = await encodeTIFF(result);
                                    ext = 'tif';
                                }
                                if (!blob) continue;

                                const filename = `${baseName}${exportSuffix}.${ext}`;
                                if (useDirectFS) {
                                    const targetFolder = format === 'jpeg' ? subFolders.jpeg : subFolders.tiff;
                                    await saveBlobToPath(targetFolder, filename.replace(/\.[^/.]+$/, ''), ext, blob);
                                } else {
                                    const targetFolder = zipFolders[format as 'jpeg' | 'tiff'];
                                    if (targetFolder) targetFolder.file(filename, blob);
                                }
                            }
                        }));
                        console.log(`Exported ${Math.min(i + batchSize, batchItems.length)}/${batchItems.length} images`);
                    }

                    if (!useDirectFS) {
                        const content = await zip.generateAsync({ type: 'blob' });
                        const url = URL.createObjectURL(content);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `${exportFolderName}.zip`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                    }
      }
      setIsProcessing(false);
  };

  const handleFlatfieldUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      try {
          setIsProcessing(true);
          const data = await loadImageFile(file);
          setFlatfieldImage(data);
      } catch(e: any) {
          alert("Error loading flatfield: " + e.message);
      } finally {
          setIsProcessing(false);
      }
  };

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
     if (transformMode) return; 

     if (!processedImage || !originalImage || !canvasRef.current) return;
     
     const rect = canvasRef.current.getBoundingClientRect();
     const scaleX = canvasRef.current.width / rect.width;
     const scaleY = canvasRef.current.height / rect.height;
     const x = Math.floor((e.clientX - rect.left) * scaleX);
     const y = Math.floor((e.clientY - rect.top) * scaleY);

     if (isPickingWB) {
        const idx = (y * processedImage.width + x) * 4;
        if (idx < 0 || idx >= processedImage.data.length) return;
        
        const r = processedImage.data[idx];
        const g = processedImage.data[idx+1];
        const b = processedImage.data[idx+2];
        
        const currentTemp = (b - r); 
        const currentTint = (g - (r+b)/2); 
        const tempCorrection = currentTemp * 0.2; 
        const tintCorrection = currentTint * 0.2;
        
        setParams(p => ({
            ...p,
            output_temp: p.output_temp + tempCorrection, 
            output_tint: p.output_tint - tintCorrection
        }));
        setIsPickingWB(false);
     }
  };

  // --- TRANSFORM LOGIC ---
  const startTransform = () => {
      setTransformMode(true);
      setIsPickingWB(false);
      setStraightenAngle(0);
      setCropRect({x: 0.05, y: 0.05, w: 0.9, h: 0.9});
  };

  const applyRotate90 = (angle: number) => {
      if (!activeItemId) return;
      
      // Update rotation in batch item
      setBatchItems(prev => prev.map(item => {
          if (item.id === activeItemId) {
              const newRotation = (item.rotation + angle) % 360;
              return { ...item, rotation: newRotation };
          }
          return item;
      }));
  };

  const applyTransform = () => {
      if (!originalImage || !activeItemId) return;
      const currentItem = batchItems.find(item => item.id === activeItemId);
      if (!currentItem) return;
      const flattened = getImageWithRotation(currentItem.imageData, currentItem.rotation || 0);
      setEditHistory(prev => [...prev, flattened]);
      const transformed = transformImage(flattened, straightenAngle, cropRect);
      setOriginalImage(transformed);
      setBatchItems(prev => prev.map(item => 
          item.id === activeItemId ? { ...item, imageData: transformed, rotation: 0 } : item
      ));
      setTransformMode(false);
  };

  // --- RENDER PIPELINE (OPTIMIZED) ---
  useEffect(() => {
    if (!originalImage || !activeItemId) return;
    
    // Get current rotation from batch item
    const currentItem = batchItems.find(item => item.id === activeItemId);
    const rotation = currentItem?.rotation || 0;
    
    // Apply rotation to original image before processing
    let imageToProcess = originalImage;
    if (rotation !== 0) {
      imageToProcess = rotateImage(originalImage, rotation);
    }
    
    // Include rotation in cache key
    const cacheKey = `${activeItemId}_rot${rotation}_${imageToProcess.width}x${imageToProcess.height}_${JSON.stringify(params)}`;
    const cached = processedImageCache.get(cacheKey);
    
    if (cached) {
      setProcessedImage(cached as ImageData);
      setIsProcessing(false);
      return;
    }

    const timer = setTimeout(() => {
      setIsProcessing(true);
      requestAnimationFrame(async () => {
                const result = processImage(imageToProcess, params, flatfieldImage);
                const output = result.output;
                const newStats = result.stats;

        setProcessedImage(output);
        setStats(newStats);
        
        // Update stats in batchItems for this image
        if (activeItemId) {
          setBatchItems(prev => prev.map(item => 
            item.id === activeItemId ? { ...item, stats: newStats } : item
          ));
        }
        
        processedImageCache.set(cacheKey, output);
        setIsProcessing(false);
      });
    }, 30);
    return () => clearTimeout(timer);
    }, [params, originalImage, flatfieldImage, activeItemId, batchItems]);

  // --- DRAW CANVAS ---
  useEffect(() => {
    if (!canvasRef.current) return;
    
    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    let displayData = showOriginal ? originalImage : processedImage;
    if (!displayData) return;

    if (transformMode && straightenAngle !== 0) {
        const rad = straightenAngle * Math.PI / 180;
        const absCos = Math.abs(Math.cos(rad));
        const absSin = Math.abs(Math.sin(rad));
        const nw = displayData.width * absCos + displayData.height * absSin;
        const nh = displayData.width * absSin + displayData.height * absCos;
        
        canvasRef.current.width = nw;
        canvasRef.current.height = nh;

        const temp = document.createElement('canvas');
        temp.width = displayData.width;
        temp.height = displayData.height;
        temp.getContext('2d')?.putImageData(displayData, 0, 0);

        ctx.translate(nw/2, nh/2);
        ctx.rotate(rad);
        ctx.drawImage(temp, -displayData.width/2, -displayData.height/2);
        ctx.resetTransform();
    } else {
        canvasRef.current.width = displayData.width;
        canvasRef.current.height = displayData.height;
        ctx.putImageData(displayData, 0, 0);
    }
    
  }, [processedImage, originalImage, showOriginal, transformMode, straightenAngle]);

  const handleUndo = () => {
      if (editHistory.length === 0) return;
      const previous = editHistory[editHistory.length - 1];
      setOriginalImage(previous);
      setEditHistory(prev => prev.slice(0, -1));
      setBatchItems(prev => prev.map(item => 
          item.id === activeItemId ? { ...item, imageData: previous } : item
      ));
  };

  const updateParam = (key: keyof ColorParams, value: number) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const handleProfileChange = (profileId: string) => {
    const profile = FILM_PROFILES.find(p => p.id === profileId);
    if (profile) {
      setSelectedProfileId(profileId);
      setParams(prev => ({
          ...profile.defaults,
          mask_r: prev.mask_r,
          mask_g: prev.mask_g,
          mask_b: prev.mask_b,
          input_temp: prev.input_temp, 
          input_tint: prev.input_tint
      }));
    }
  };

  const handleAutoAdjust = () => {
    if (!originalImage) return;
    const suggestions = analyzeNegative(originalImage, analysisPadding);
    setParams(prev => ({ ...prev, ...suggestions }));
  };

  const handleCopyParams = () => {
    setCopiedParams({ ...params });
  };

  const handlePasteParams = () => {
    if (!copiedParams) return;
    setParams({ ...copiedParams });
    
    // Update the active batch item with pasted params
    if (activeItemId) {
      setBatchItems(prev => prev.map(item => 
        item.id === activeItemId ? { ...item, params: { ...copiedParams } } : item
      ));
    }
  };

  const handleSyncCrop = async () => {
    if (!savedCrop) {
      // Save current crop settings
      setSavedCrop({ angle: straightenAngle, rect: { ...cropRect } });
      return;
    }

    setIsProcessing(true);

    // Get the ID of the image that was already cropped
    const alreadyCroppedId = activeItemId;

    // Apply crop to all batch items except the one already cropped
    const updatedItems = await Promise.all(
      batchItems.map(async (item) => {
        // Skip the image that was already manually cropped
        if (item.id === alreadyCroppedId) {
          return item;
        }

        const flattened = getImageWithRotation(item.imageData, item.rotation || 0);
        const cropped = transformImage(flattened, savedCrop.angle, savedCrop.rect);
        
        return {
          ...item,
          imageData: cropped,
          rotation: 0,
        };
      })
    );

    setBatchItems(updatedItems);

    setIsProcessing(false);
    setSavedCrop(null);
  };

  const handleReconvertCurrent = () => {
    // Reset current image to default params
    setParams({ ...DEFAULT_PARAMS });
    
    // Update in batch items
    if (activeItemId) {
      setBatchItems(prev => prev.map(item => 
        item.id === activeItemId ? { ...item, params: { ...DEFAULT_PARAMS } } : item
      ));
    }
  };

  const handleReconvertAll = async () => {
    setIsProcessing(true);

    // Reset all batch items to default params
    setBatchItems(prev => prev.map(item => ({
      ...item,
      params: { ...DEFAULT_PARAMS }
    })));

    // Update current image params
    setParams({ ...DEFAULT_PARAMS });
    
    // Clear processed images tracking
    setProcessedImageIds(new Set());

    setIsProcessing(false);
  };

  const handleNextImage = () => {
    if (!activeItemId) return;
    
    // Mark current image as processed
    setProcessedImageIds(prev => new Set(prev).add(activeItemId));
    
    // Find current index
    const currentIndex = batchItems.findIndex(item => item.id === activeItemId);
    
    // Move to next image if not at the end
    if (currentIndex < batchItems.length - 1) {
      selectBatchItem(batchItems[currentIndex + 1]);
    }
  };

  const isLastImage = () => {
    if (!activeItemId || batchItems.length === 0) return false;
    const currentIndex = batchItems.findIndex(item => item.id === activeItemId);
    return currentIndex === batchItems.length - 1;
  };

  // Crop Drag Logic
  const handleCropDrag = (e: React.MouseEvent | React.TouchEvent) => {
      if (!isDraggingCrop || !overlayRef.current) return;
      
      const rect = overlayRef.current.getBoundingClientRect();
      const clientX = 'touches' in e ? e.touches[0].clientX : (e as React.MouseEvent).clientX;
      const clientY = 'touches' in e ? e.touches[0].clientY : (e as React.MouseEvent).clientY;
      
      const x = (clientX - rect.left) / rect.width;
      const y = (clientY - rect.top) / rect.height;
      
      const dx = x - (window as any).lastCropX;
      const dy = y - (window as any).lastCropY;
      (window as any).lastCropX = x;
      (window as any).lastCropY = y;
      
      setCropRect(prev => {
          let { x: px, y: py, w: pw, h: ph } = prev;
          
          if (isDraggingCrop === 'move') {
              px += dx; py += dy;
          } else if (isDraggingCrop === 'br') {
              pw += dx; ph += dy;
          } else if (isDraggingCrop === 'tl') {
              px += dx; py += dy; pw -= dx; ph -= dy;
          } else if (isDraggingCrop === 'tr') {
              py += dy; pw += dx; ph -= dy;
          } else if (isDraggingCrop === 'bl') {
              px += dx; pw -= dx; ph += dy;
          }
          
          // Constraints
          if (pw < 0.1) pw = 0.1;
          if (ph < 0.1) ph = 0.1;
          if (px < 0) px = 0;
          if (py < 0) py = 0;
          if (px + pw > 1) {
               if (isDraggingCrop === 'move') px = 1 - pw;
               else pw = 1 - px;
          }
          if (py + ph > 1) {
               if (isDraggingCrop === 'move') py = 1 - ph;
               else ph = 1 - py;
          }
          
          return { x: px, y: py, w: pw, h: ph };
      });
  };
  
  const startCropDrag = (mode: any, e: React.MouseEvent | React.TouchEvent) => {
      setIsDraggingCrop(mode);
      const clientX = 'touches' in e ? e.touches[0].clientX : (e as React.MouseEvent).clientX;
      const clientY = 'touches' in e ? e.touches[0].clientY : (e as React.MouseEvent).clientY;
      const rect = overlayRef.current?.getBoundingClientRect();
      if(rect) {
          (window as any).lastCropX = (clientX - rect.left) / rect.width;
          (window as any).lastCropY = (clientY - rect.top) / rect.height;
      }
  };

  return (
    <div className="flex h-screen bg-[#09090b] text-gray-100 overflow-hidden font-sans select-none" 
         onMouseMove={(e) => isDraggingCrop && handleCropDrag(e)}
         onMouseUp={() => setIsDraggingCrop(null)}
         onTouchMove={(e) => isDraggingCrop && handleCropDrag(e)}
         onTouchEnd={() => setIsDraggingCrop(null)}
    >
      {/* EXPORT MODAL */}
      {showExportModal && (
          <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 backdrop-blur-sm">
              <div className="bg-[#18181b] border border-white/10 rounded-xl w-full max-w-md p-6 shadow-2xl">
                  <h2 className="text-lg font-bold text-white flex items-center gap-2 mb-6">
                          <Download size={20} className="text-blue-500" />
                          {batchItems.length > 1 ? "Export Batch" : "Export Image"}
                  </h2>
                  <div className="space-y-4">
                      <div>
                          <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Export Directory</label>
                          <div className="flex gap-2">
                              <input 
                                    type="text" 
                                    value={exportDirectory} 
                                    onChange={e => setExportDirectory(e.target.value)}
                                    placeholder="Leave empty for default Downloads"
                                    className="flex-1 bg-[#27272a] border border-gray-700 rounded px-3 py-2 text-white text-xs"
                              />
                              <button 
                                    onClick={async () => {
                                        if (window.electronAPI) {
                                            const path = await window.electronAPI.openDirectoryDialog();
                                            if (path) setExportDirectory(path);
                                        } else {
                                            alert('Directory selection not available in browser mode');
                                        }
                                    }}
                                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-bold"
                              >
                                  Browse
                              </button>
                          </div>
                      </div>
                      <div>
                          <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Folder Name</label>
                          <input 
                                type="text" 
                                value={exportFolderName} 
                                onChange={e => setExportFolderName(e.target.value)}
                                className="w-full bg-[#27272a] border border-gray-700 rounded px-3 py-2 text-white"
                          />
                      </div>
                      <div>
                          <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Format (Select Multiple)</label>
                          <div className="grid grid-cols-2 gap-3">
                              <button 
                                  onClick={() => {
                                      const newFormats = new Set(exportFormats);
                                      if (newFormats.has('jpeg')) newFormats.delete('jpeg');
                                      else newFormats.add('jpeg');
                                      setExportFormats(newFormats);
                                  }} 
                                  className={`py-2 rounded text-xs font-bold border ${
                                      exportFormats.has('jpeg') 
                                          ? 'bg-blue-600 border-blue-500 text-white' 
                                          : 'bg-[#27272a] border-gray-700 text-gray-400'
                                  }`}
                              >
                                  JPEG
                              </button>
                              <button 
                                  onClick={() => {
                                      const newFormats = new Set(exportFormats);
                                      if (newFormats.has('tiff')) newFormats.delete('tiff');
                                      else newFormats.add('tiff');
                                      setExportFormats(newFormats);
                                  }} 
                                  className={`py-2 rounded text-xs font-bold border ${
                                      exportFormats.has('tiff') 
                                          ? 'bg-blue-600 border-blue-500 text-white' 
                                          : 'bg-[#27272a] border-gray-700 text-gray-400'
                                  }`}
                              >
                                  TIFF
                              </button>
                          </div>
                      </div>
                      {exportFormats.has('jpeg') && (
                          <div>
                              <label className="block text-xs font-bold text-gray-400 uppercase mb-2">JPEG Quality: {(exportQuality * 100).toFixed(0)}%</label>
                              <input type="range" min="0.1" max="1.0" step="0.05" value={exportQuality} onChange={e => setExportQuality(parseFloat(e.target.value))} className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer" />
                          </div>
                      )}
                      <div>
                          <label className="block text-xs font-bold text-gray-400 uppercase mb-2">Filename Suffix</label>
                          <input 
                                type="text" value={exportName || exportSuffix} 
                                onChange={e => batchItems.length>1 ? setExportSuffix(e.target.value) : setExportName(e.target.value)}
                                className="w-full bg-[#27272a] border border-gray-700 rounded px-3 py-2 text-white"
                          />
                      </div>
                      <div className="flex gap-3 mt-8">
                        <button onClick={() => setShowExportModal(false)} className="flex-1 py-2.5 rounded bg-[#27272a] hover:bg-[#3f3f46]">Cancel</button>
                        <button onClick={performExport} className="flex-1 py-2.5 rounded bg-blue-600 hover:bg-blue-500 text-white">Save</button>
                      </div>
                  </div>
              </div>
          </div>
      )}

      {/* LEFT SIDEBAR */}
      <aside className="w-80 flex flex-col border-r border-white/10 bg-[#121214] z-10 shadow-xl">
        <div className="p-4 border-b border-white/10 bg-[#18181b] flex items-center justify-between">
          <h1 className="text-sm font-bold tracking-wider text-white flex items-center gap-2 uppercase">
            <span className="w-2 h-2 rounded-full bg-orange-500"></span>
            Analoga
          </h1>
        </div>
        
        {/* Navigation Toggles */}
        <div className="p-2 grid grid-cols-2 gap-2 border-b border-white/10">
            <button 
                onClick={() => setViewMode('library')} 
                className={`flex flex-col items-center gap-1 py-3 rounded-lg transition-colors ${viewMode === 'library' ? 'bg-[#27272a] text-white' : 'text-gray-500 hover:text-gray-300'}`}
            >
                <Database size={18} />
                <span className="text-[10px] font-bold uppercase">Library</span>
            </button>
            <button 
                onClick={() => setViewMode('develop')} 
                className={`flex flex-col items-center gap-1 py-3 rounded-lg transition-colors ${viewMode === 'develop' ? 'bg-[#27272a] text-white' : 'text-gray-500 hover:text-gray-300'}`}
            >
                <ImageIcon size={18} />
                <span className="text-[10px] font-bold uppercase">Develop</span>
            </button>
        </div>

        {viewMode === 'develop' ? (
            <>
                <div className="p-4 grid grid-cols-1 gap-2 border-b border-white/10">
                   <button onClick={handleAutoAdjust} className="col-span-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white text-[10px] font-bold py-2.5 rounded shadow-lg"><Wand2 size={14} /> AUTO BALANCE</button>
                   <div className="grid grid-cols-2 gap-2">
                     <button onClick={handleCopyParams} className="flex items-center justify-center gap-2 bg-gray-700 hover:bg-gray-600 text-white text-[10px] font-bold py-2 rounded"><Copy size={12} /> COPY</button>
                     <button onClick={handlePasteParams} disabled={!copiedParams} className={`flex items-center justify-center gap-2 text-[10px] font-bold py-2 rounded ${copiedParams ? 'bg-green-700 hover:bg-green-600 text-white' : 'bg-gray-800 text-gray-600 cursor-not-allowed'}`}><Clipboard size={12} /> PASTE</button>
                   </div>
                   <button onClick={handleSyncCrop} className={`flex items-center justify-center gap-2 text-[10px] font-bold py-2 rounded ${savedCrop ? 'bg-orange-600 hover:bg-orange-500 text-white' : 'bg-gray-700 hover:bg-gray-600 text-white'}`}>
                     <CropIcon size={12} /> {savedCrop ? 'APPLY CROP TO ALL' : 'SAVE CROP'}
                   </button>
                   <div className="grid grid-cols-2 gap-2">
                     <button onClick={handleReconvertCurrent} className="flex items-center justify-center gap-2 bg-purple-700 hover:bg-purple-600 text-white text-[10px] font-bold py-2 rounded">
                       <RefreshCw size={12} /> RESET
                     </button>
                     <button onClick={handleReconvertAll} className="flex items-center justify-center gap-2 bg-purple-700 hover:bg-purple-600 text-white text-[10px] font-bold py-2 rounded">
                       <RefreshCw size={12} /> RESET ALL
                     </button>
                   </div>
                </div>

                <div className="p-4 border-b border-white/10">
                  <div className="mb-2 flex justify-between text-[10px] uppercase text-gray-500 font-bold tracking-wider"><span>Histogram</span><span>RGB</span></div>
                  {stats && <Histogram data={stats.histogram} height={60} />}
                </div>

                <div className="flex bg-[#0f0f11] p-1 border-b border-white/10">
                  <button onClick={() => setActiveTab('basic')} className={`flex-1 py-2 flex flex-col items-center gap-1 text-[10px] font-bold uppercase rounded ${activeTab === 'basic' ? 'bg-[#27272a] text-blue-400' : 'text-gray-500'}`}><SlidersHorizontal size={14} /> Basic</button>
                  <button onClick={() => setActiveTab('calibration')} className={`flex-1 py-2 flex flex-col items-center gap-1 text-[10px] font-bold uppercase rounded ${activeTab === 'calibration' ? 'bg-[#27272a] text-orange-400' : 'text-gray-500'}`}><Palette size={14} /> Calibrate</button>
                </div>

                <div className="flex-1 overflow-y-auto p-5 space-y-8 scrollbar-thin pb-32">
                    {activeTab === 'basic' && (
                     <div className="space-y-6 animate-in fade-in">
                       <section>
                          <h3 className="text-[10px] font-bold text-blue-400 uppercase mb-3">Exposure & Dynamics</h3>
                          <Slider label="Dynamics" value={params.dynamic_compression} min={-25.0} max={25.0} step={0.1} onChange={v => updateParam('dynamic_compression', v)} />
                          <Slider label="Exposure" value={params.exposure} min={-3.0} max={3.0} step={0.1} onChange={v => updateParam('exposure', v)} />
                          <Slider label="Brightness" value={params.brightness} min={-1.0} max={1.0} step={0.01} onChange={v => updateParam('brightness', v)} />
                       </section>
                       <section className="pt-4 border-t border-white/5">
                          <h3 className="text-[10px] font-bold text-yellow-400 uppercase mb-3">Light Source (Input)</h3>
                          <Slider label="Temp" value={params.input_temp} min={-150} max={150} step={0.1} onChange={v => updateParam('input_temp', v)} />
                          <Slider label="Tint" value={params.input_tint} min={-150} max={150} step={0.1} onChange={v => updateParam('input_tint', v)} />
                          
                          <div className="mt-4 bg-yellow-500/5 p-3 rounded border border-yellow-500/10">
                             <h4 className="text-[9px] font-bold text-yellow-200/70 uppercase mb-2">Fine Tune (Output Tone)</h4>
                             <div className="space-y-3">
                                <div>
                                   <span className="text-[9px] uppercase text-gray-500 font-bold block mb-1">Highlight</span>
                                   <Slider label="Temp" value={params.wb_highlight_temp} min={-100} max={100} step={0.1} onChange={v => updateParam('wb_highlight_temp', v)} />
                                   <Slider label="Tint" value={params.wb_highlight_tint} min={-100} max={100} step={0.1} onChange={v => updateParam('wb_highlight_tint', v)} />
                                </div>
                                <div className="pt-2 border-t border-white/5">
                                   <span className="text-[9px] uppercase text-gray-500 font-bold block mb-1">Shadow</span>
                                   <Slider label="Temp" value={params.wb_shadow_temp} min={-100} max={100} step={0.1} onChange={v => updateParam('wb_shadow_temp', v)} />
                                   <Slider label="Tint" value={params.wb_shadow_tint} min={-100} max={100} step={0.1} onChange={v => updateParam('wb_shadow_tint', v)} />
                                </div>
                             </div>
                          </div>
                       </section>
                       <section className="pt-4 border-t border-white/5">
                          <h3 className="text-[10px] font-bold text-purple-400 uppercase mb-3">Levels & Curve</h3>
                          <Slider label="Gamma" value={params.gamma} min={0.5} max={2.0} step={0.01} onChange={v => updateParam('gamma', v)} />
                          <Slider label="Smoothing" value={params.tone_smoothing} min={0} max={1.0} onChange={v => updateParam('tone_smoothing', v)} />
                          
                          {/* RE-ADDED HIGHLIGHTS AND SHADOWS SLIDERS */}
                          <div className="grid grid-cols-2 gap-3 mt-2 border-t border-white/5 pt-2">
                               <Slider label="Highlights" value={params.highlights} min={-1.0} max={1.0} step={0.01} onChange={v => updateParam('highlights', v)} />
                               <Slider label="Shadows" value={params.shadows} min={-1.0} max={1.0} step={0.01} onChange={v => updateParam('shadows', v)} />
                          </div>

                          <div className="grid grid-cols-2 gap-3 mt-2 border-t border-white/5 pt-2">
                             <Slider label="Black Pt" value={params.black_point} min={0} max={0.2} step={0.001} onChange={v => updateParam('black_point', v)} />
                             <Slider label="White Pt" value={params.white_point} min={0.5} max={1.2} step={0.001} onChange={v => updateParam('white_point', v)} />
                          </div>
                       </section>
                       <section className="pt-4 border-t border-white/5">
                          <h3 className="text-[10px] font-bold text-pink-500 uppercase mb-3">Finishing</h3>
                          <Slider label="Saturation" value={params.saturation} min={0} max={2} step={0.01} onChange={v => updateParam('saturation', v)} />
                          <Slider label="Vibrance" value={params.vibrance} min={0} max={1.0} step={0.01} onChange={v => updateParam('vibrance', v)} />
                          <Slider label="Sharpening" value={params.sharpening} min={0} max={2.0} step={0.01} onChange={v => updateParam('sharpening', v)} />
                       </section>
                     </div>
                    )}
                    {activeTab === 'calibration' && (
                     <div className="space-y-6 animate-in fade-in">
                        <div className="bg-orange-500/5 border border-orange-500/20 p-3 rounded">
                          <h3 className="text-[10px] font-bold text-orange-400 uppercase mb-2">Negative Calibration</h3>
                      </div>
                      
                      {/* RE-ADDED CALIBRATION BUTTON */}
                      <button onClick={handleAutoAdjust} className="w-full flex items-center justify-center gap-2 bg-gray-700 hover:bg-gray-600 text-white py-2 rounded font-bold text-xs transition-colors mt-2 mb-2">
                        <Wand2 size={14} /> Auto-Analyze Frame
                      </button>
                      <section className="bg-gray-900 p-3 rounded border border-gray-800">
                         <h3 className="text-[10px] font-bold text-gray-300 uppercase mb-2 flex items-center gap-2"><Droplet size={12} /> Flatfield Correction</h3>
                         <input type="file" accept="image/*,.dng,.tif,.arw" className="hidden" ref={flatfieldInputRef} onChange={handleFlatfieldUpload} />
                         {!flatfieldImage ? (
                             <button onClick={() => flatfieldInputRef.current?.click()} className="w-full py-2 border border-dashed border-gray-600 text-gray-500 text-xs rounded hover:border-gray-400">+ Load Reference</button>
                         ) : (
                             <div className="flex items-center justify-between bg-green-900/20 p-2 rounded border border-green-900/50"><span className="text-xs text-green-400 font-medium">Reference Loaded</span><button onClick={() => setFlatfieldImage(null)} className="text-xs text-red-400 underline">Clear</button></div>
                         )}
                      </section>
                      <div className="bg-gray-900 p-3 rounded border border-gray-800">
                          <div className="flex justify-between items-center mb-2"><span className="text-[10px] font-bold uppercase text-gray-300">Analysis Buffer</span><span className="text-[10px] font-mono text-blue-400">{(analysisPadding * 100).toFixed(0)}%</span></div>
                          <Slider label="Edge Ignore" value={analysisPadding} min={0} max={0.45} step={0.01} onChange={setAnalysisPadding} />
                      </div>
                      <section>
                          <h3 className="text-[10px] font-bold text-gray-500 uppercase mb-3">Film Mask (Base)</h3>
                          <Slider label="Red" value={params.mask_r} min={0} max={2.0} step={0.01} onChange={v => updateParam('mask_r', v)} />
                          <Slider label="Green" value={params.mask_g} min={0} max={2.0} step={0.01} onChange={v => updateParam('mask_g', v)} />
                          <Slider label="Blue" value={params.mask_b} min={0} max={2.0} step={0.01} onChange={v => updateParam('mask_b', v)} />
                      </section>
                      <div className="bg-white/5 p-3 rounded-lg border border-white/5 mt-4">
                          <h3 className="text-[10px] font-bold text-gray-400 uppercase mb-4 flex items-center gap-2"><div className="w-1 h-3 bg-green-500 rounded-full"></div>Scanner Color (CMY)</h3>
                          <div className="space-y-4">
                            <Slider label="Cyan / Red" value={params.cyan_red} min={-20} max={20} step={0.1} onChange={v => updateParam('cyan_red', v)} />
                            <Slider label="Magenta / Green" value={params.magenta_green} min={-20} max={20} step={0.1} onChange={v => updateParam('magenta_green', v)} />
                            <Slider label="Yellow / Blue" value={params.yellow_blue} min={-20} max={20} step={0.1} onChange={v => updateParam('yellow_blue', v)} />
                          </div>
                       </div>
                       <div className="mt-6">
                        <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider block mb-2">Profile</label>
                        <select value={selectedProfileId} onChange={(e) => handleProfileChange(e.target.value)} className="w-full bg-[#1f1f22] border border-gray-700 text-gray-300 text-xs rounded px-3 py-2">{FILM_PROFILES.map(p => (<option key={p.id} value={p.id}>{p.name}</option>))}</select>
                      </div>
                     </div>
                    )}
                </div>
            </>
        ) : (
            // LIBRARY SIDEBAR CONTENT (Just informational text)
            <div className="p-5 text-gray-500 text-xs">
                <p>Select a root folder containing your client orders.</p>
                <p className="mt-2 text-gray-600">Expected Structure:</p>
                <ul className="mt-1 ml-2 list-disc space-y-1 text-gray-600 font-mono">
                    <li>/Root</li>
                    <li>../Order_A</li>
                    <li>..../Roll_1</li>
                    <li>....../img.raw</li>
                </ul>
            </div>
        )}
      </aside>

      {/* MAIN AREA */}
      <main className="flex-1 bg-[#050505] relative flex flex-col min-w-0">
        {viewMode === 'library' ? (
            // --- MEDIA LIBRARY VIEW ---
            <div className="flex-1 p-8 overflow-y-auto">
                <div className="max-w-4xl mx-auto">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h2 className="text-2xl font-bold text-white mb-1">Media Library</h2>
                            <p className="text-gray-400 text-sm">Manage orders and film rolls.</p>
                        </div>
                        {/* Folder Input Hack for Directory Selection */}
                        <input 
                            type="file" 
                            ref={folderInputRef} 
                            onChange={handleFolderSelect} 
                            className="hidden"
                            {...{webkitdirectory:"", directory:""} as any} 
                        />
                        <button 
                            onClick={() => folderInputRef.current?.click()} 
                            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-lg font-bold text-sm transition-colors"
                        >
                            <FolderOpen size={18} /> Open Root Folder
                        </button>
                    </div>

                    {mediaLibrary.length === 0 ? (
                        <div className="border-2 border-dashed border-white/10 rounded-xl p-12 text-center">
                            <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-4 text-gray-500"><FolderOpen size={32} /></div>
                            <h3 className="text-lg font-medium text-gray-300">No Folder Selected</h3>
                            <p className="text-gray-500 mt-2">Point the app to your "Lab Scans" or "Orders" folder to begin.</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {mediaLibrary.map(order => (
                                <div key={order.id} className="bg-[#121214] border border-white/10 rounded-lg overflow-hidden">
                                    <button 
                                        onClick={() => toggleOrderExpand(order.id)}
                                        className="w-full flex items-center justify-between p-4 bg-[#18181b] hover:bg-[#202023] transition-colors text-left"
                                    >
                                        <div className="flex items-center gap-3">
                                            {expandedOrders.has(order.id) ? <ChevronDown size={16} className="text-gray-500" /> : <ChevronRight size={16} className="text-gray-500" />}
                                            <span className="font-bold text-gray-200">{order.name}</span>
                                            <span className="text-xs bg-white/5 px-2 py-1 rounded text-gray-500">{order.rolls.length} Rolls</span>
                                        </div>
                                    </button>
                                    
                                    {expandedOrders.has(order.id) && (
                                        <div className="p-2 bg-[#0e0e10]">
                                            {order.rolls.map(roll => (
                                                <div key={roll.id} className="flex items-center justify-between p-3 hover:bg-white/5 rounded mb-1">
                                                    <div className="flex items-center gap-3">
                                                        <div className="w-8 h-8 bg-blue-900/30 text-blue-400 rounded flex items-center justify-center"><Film size={16} /></div>
                                                        <div>
                                                            <div className="text-sm font-medium text-gray-300">{roll.name}</div>
                                                            <div className="text-xs text-gray-500">{roll.fileCount} images</div>
                                                        </div>
                                                    </div>
                                                    <button 
                                                        onClick={() => loadRollToEditor(roll)}
                                                        className="flex items-center gap-2 bg-green-600/20 hover:bg-green-600/40 text-green-400 border border-green-600/30 px-3 py-1.5 rounded text-xs font-bold transition-colors"
                                                    >
                                                        <Play size={12} fill="currentColor" /> Load to Editor
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        ) : (
            // --- DEVELOP / EDITOR VIEW ---
            <>
                {/* TOP BAR */}
                <div className="h-14 border-b border-white/10 bg-[#09090b] flex items-center px-4 justify-between z-20">
                  <div className="flex items-center gap-3">
                    <input type="file" accept="image/*,.dng,.tif,.tiff,.arw,.cr2,.nef" multiple className="hidden" ref={fileInputRef} onChange={handleFileUpload} />
                    <button onClick={() => fileInputRef.current?.click()} className="flex items-center gap-2 bg-white/5 hover:bg-white/10 text-gray-300 px-3 py-2 rounded text-xs font-bold transition-colors"><Upload size={14} /> Add Files</button>
                    {batchItems.length > 0 && <span className="text-xs text-gray-500 font-medium border-l border-white/10 pl-3">{batchItems.length} items active</span>}
                    
                    {originalImage && (
                        <div className="flex items-center gap-2 ml-4 pl-4 border-l border-white/10">
                            {/* ROTATION BUTTONS (Always visible) */}
                            <div className="flex items-center gap-1 bg-white/5 px-2 py-1 rounded">
                                <button onClick={() => applyRotate90(-90)} className="p-1.5 text-gray-300 hover:text-white hover:bg-white/10 rounded transition-colors" title="Rotate 90° Left">
                                    <RotateLeft size={16} />
                                </button>
                                <div className="h-4 w-px bg-white/10"></div>
                                <button onClick={() => applyRotate90(90)} className="p-1.5 text-gray-300 hover:text-white hover:bg-white/10 rounded transition-colors" title="Rotate 90° Right">
                                    <RotateCw size={16} />
                                </button>
                            </div>

                            {/* CROP TOOL */}
                            <button
                                onClick={startTransform}
                                className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-bold transition-colors ${transformMode ? 'bg-green-500 text-white' : 'bg-white/5 text-gray-400 hover:text-white'}`}
                                title="Crop & Straighten"
                            >
                                <CropIcon size={14} /> Crop
                            </button>

                            <button
                                onClick={() => setIsPickingWB(prev => !prev)}
                                className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-bold transition-colors ${isPickingWB ? 'bg-blue-600 text-white' : 'bg-white/5 text-gray-400 hover:text-white'}`}
                                title="Pick white balance from image"
                            >
                                <Pipette size={14} /> WB Pick
                            </button>

                            <button onClick={handleUndo} disabled={editHistory.length === 0} className={`p-1.5 rounded ${editHistory.length > 0 ? 'text-white hover:bg-white/10' : 'text-gray-700 cursor-not-allowed'}`} title="Undo">
                                <RotateCcw size={14} />
                            </button>
                        </div>
                    )}
                  </div>
                  
                  {/* TRANSFORM CONTROLS (When Active) */}
                  {transformMode ? (
                      <div className="flex items-center gap-4 animate-in fade-in slide-in-from-top-2">
                          <div className="flex items-center gap-2">
                              <span className="text-[10px] uppercase font-bold text-gray-500">Straighten</span>
                              <input type="range" min="-25" max="25" step="0.1" value={straightenAngle} onChange={e => setStraightenAngle(parseFloat(e.target.value))} className="w-32 h-1 bg-gray-700 rounded" />
                              <span className="text-[10px] font-mono text-gray-400 w-8 text-right">{straightenAngle.toFixed(1)}°</span>
                          </div>
                          <div className="flex items-center gap-2 ml-2">
                              <button onClick={() => setTransformMode(false)} className="p-1.5 text-red-400 hover:bg-red-500/20 rounded"><X size={18} /></button>
                              <button onClick={applyTransform} className="p-1.5 text-green-400 hover:bg-green-500/20 rounded"><Check size={18} /></button>
                          </div>
                      </div>
                  ) : (
                    <div className="flex items-center gap-3">
                        {/* Performance Indicator */}
                        <div className="flex items-center gap-2 text-xs bg-white/5 px-2 py-1 rounded border border-white/10">
                            <span className="text-blue-400 flex items-center gap-1">
                                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                                CPU
                            </span>
                        </div>
                        
                        {isProcessing && <span className="text-xs text-orange-500 font-mono animate-pulse mr-4">PROCESSING...</span>}
                        {originalImage && (
                            <button onMouseDown={() => setShowOriginal(true)} onMouseUp={() => setShowOriginal(false)} onMouseLeave={() => setShowOriginal(false)} className="flex items-center gap-2 bg-white/5 hover:bg-white/10 text-gray-200 px-3 py-1.5 rounded border border-white/5 text-xs font-medium transition-colors mr-2">
                                <Eye size={14} /> Compare
                            </button>
                        )}
                        {batchItems.length > 0 && <button onClick={openExportModal} className="flex items-center gap-2 px-4 py-2 rounded text-xs font-bold transition-colors bg-white text-black hover:bg-gray-200"><Download size={14} /> {batchItems.length > 1 ? "Download Batch" : "Save Image"}</button>}
                    </div>
                  )}
                </div>

                {/* CANVAS AREA */}
                <div className="flex-1 overflow-auto flex items-center justify-center p-8 bg-[radial-gradient(circle_at_center,_#1a1a1a_0%,_#000000_100%)] pb-40">
                  {!originalImage ? (
                     <div className="text-center text-gray-600">
                       <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-4"><Film size={32} className="opacity-40" /></div>
                       <h2 className="text-lg font-medium text-gray-400">No Film Loaded</h2>
                       <p className="text-xs text-gray-600 mt-2">Go to Library to import rolls</p>
                     </div>
                  ) : (
                     <div className="relative shadow-2xl shadow-black border border-white/10 inline-block">
                       <canvas ref={canvasRef} onClick={handleCanvasClick} className={`max-w-full max-h-[65vh] block ${isPickingWB ? 'cursor-crosshair' : ''}`} />
                       
                       {/* Transform Overlay */}
                       {transformMode && (
                           <div ref={overlayRef} className="absolute inset-0 z-10 cursor-move"
                               onMouseDown={(e) => startCropDrag('move', e)}
                               onTouchStart={(e) => startCropDrag('move', e)}
                           >
                               {/* Dimmed Areas */}
                               <div className="absolute bg-black/50 top-0 left-0 right-0" style={{height: `${cropRect.y * 100}%`}}></div>
                               <div className="absolute bg-black/50 bottom-0 left-0 right-0" style={{height: `${(1 - (cropRect.y + cropRect.h)) * 100}%`}}></div>
                               <div className="absolute bg-black/50 top-0 bottom-0 left-0" style={{width: `${cropRect.x * 100}%`, top: `${cropRect.y * 100}%`, bottom: `${(1-(cropRect.y+cropRect.h))*100}%`}}></div>
                               <div className="absolute bg-black/50 top-0 bottom-0 right-0" style={{width: `${(1 - (cropRect.x + cropRect.w)) * 100}%`, top: `${cropRect.y * 100}%`, bottom: `${(1-(cropRect.y+cropRect.h))*100}%`}}></div>
                               
                               {/* Crop Box */}
                               <div className="absolute border border-white shadow-[0_0_0_1px_rgba(0,0,0,0.5)]"
                                   style={{
                                       left: `${cropRect.x * 100}%`,
                                       top: `${cropRect.y * 100}%`,
                                       width: `${cropRect.w * 100}%`,
                                       height: `${cropRect.h * 100}%`
                                   }}
                               >
                                   {/* Grid Lines */}
                                   <div className="absolute inset-0 flex flex-col">
                                       <div className="flex-1 border-b border-white/30"></div>
                                       <div className="flex-1 border-b border-white/30"></div>
                                       <div className="flex-1"></div>
                                   </div>
                                   <div className="absolute inset-0 flex">
                                       <div className="flex-1 border-r border-white/30"></div>
                                       <div className="flex-1 border-r border-white/30"></div>
                                       <div className="flex-1"></div>
                                   </div>

                                   {/* Handles */}
                                   <div className="absolute -top-1.5 -left-1.5 w-3 h-3 bg-white border border-black cursor-nw-resize z-20" onMouseDown={(e) => {e.stopPropagation(); startCropDrag('tl', e)}} onTouchStart={(e) => {e.stopPropagation(); startCropDrag('tl', e)}}></div>
                                   <div className="absolute -top-1.5 -right-1.5 w-3 h-3 bg-white border border-black cursor-ne-resize z-20" onMouseDown={(e) => {e.stopPropagation(); startCropDrag('tr', e)}} onTouchStart={(e) => {e.stopPropagation(); startCropDrag('tr', e)}}></div>
                                   <div className="absolute -bottom-1.5 -left-1.5 w-3 h-3 bg-white border border-black cursor-sw-resize z-20" onMouseDown={(e) => {e.stopPropagation(); startCropDrag('bl', e)}} onTouchStart={(e) => {e.stopPropagation(); startCropDrag('bl', e)}}></div>
                                   <div className="absolute -bottom-1.5 -right-1.5 w-3 h-3 bg-white border border-black cursor-se-resize z-20" onMouseDown={(e) => {e.stopPropagation(); startCropDrag('br', e)}} onTouchStart={(e) => {e.stopPropagation(); startCropDrag('br', e)}}></div>
                               </div>
                           </div>
                       )}

                       {/* Analysis Overlay */}
                       {activeTab === 'calibration' && !transformMode && (
                          <div className="absolute border-2 border-red-500/50 border-dashed pointer-events-none" style={{ top: `${analysisPadding * 100}%`, left: `${analysisPadding * 100}%`, right: `${analysisPadding * 100}%`, bottom: `${analysisPadding * 100}%` }}></div>
                       )}
                       
                       {showOriginal && <div className="absolute top-4 left-4 bg-white text-black px-2 py-1 rounded text-xs font-bold uppercase tracking-widest opacity-80 pointer-events-none">Original</div>}
                     </div>
                  )}
                </div>
                {/* Filmstrip (Existing) */}
                {batchItems.length > 0 && (
                    <div className="absolute bottom-0 left-0 right-0 h-36 bg-[#121214] border-t border-white/10 flex flex-col z-30">
                        <div className="h-8 bg-[#18181b] flex items-center px-4 justify-between border-b border-white/5"><span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">Film Strip</span></div>
                        <div className="flex-1 overflow-x-auto flex items-center gap-2 p-3 pr-2 scrollbar-thin">
                            {batchItems.map(item => (
                                <div key={item.id} className="relative group flex-shrink-0">
                                    <button onClick={() => selectBatchItem(item)} className={`w-24 h-20 rounded overflow-hidden border-2 transition-all ${
                                        activeItemId === item.id 
                                            ? 'border-blue-500' 
                                            : processedImageIds.has(item.id)
                                                ? 'border-green-500'
                                                : 'border-transparent hover:border-gray-600'
                                    }`}>
                                        <img src={item.thumbnail} alt="" className="w-full h-full object-cover" />
                                        {activeItemId === item.id && <div className="absolute top-1 right-1 bg-blue-500 w-3 h-3 rounded-full border border-black"></div>}
                                    </button>
                                    <button 
                                        onClick={(e) => { e.stopPropagation(); removeBatchItem(item.id); }}
                                        className="absolute -top-2 -right-2 w-5 h-5 bg-red-600 hover:bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                                        title="Remove image"
                                    >
                                        <X size={12} />
                                    </button>
                                </div>
                            ))}
                            <button onClick={() => fileInputRef.current?.click()} className="flex-shrink-0 w-24 h-20 rounded border border-white/10 bg-white/5 hover:bg-white/10 flex flex-col items-center justify-center gap-1 text-gray-500"><Upload size={16} /><span className="text-[9px] font-bold uppercase">Add</span></button>
                            
                            {/* Next / Export Button in Filmstrip */}
                            {activeItemId && (
                                <div className="flex-shrink-0 ml-2 pl-2 border-l border-white/10">
                                    {isLastImage() ? (
                                        <button 
                                            onClick={openExportModal} 
                                            className="w-24 h-20 flex flex-col items-center justify-center gap-1 bg-green-600 hover:bg-green-500 text-white rounded text-xs font-bold transition-colors"
                                        >
                                            <Download size={18} />
                                            <span className="text-[10px] uppercase">Export</span>
                                        </button>
                                    ) : (
                                        <button 
                                            onClick={handleNextImage} 
                                            className="w-24 h-20 flex flex-col items-center justify-center gap-1 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-bold transition-colors"
                                        >
                                            <ChevronRight size={18} />
                                            <span className="text-[10px] uppercase">Next</span>
                                        </button>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </>
        )}
      </main>
    </div>
  );
};

export default App;