# Photo Editor

A professional image editing application built with Python, PyQt5 and OpenCV.

**Author:** [D-speedster](https://github.com/D-speedster)

## Features

### Basic Features
- Open/Save images (PNG, JPG, BMP, TIFF)
- Webcam capture with live preview
- Undo/Redo (10 steps)
- Zoom In/Out

### Filters
- Blur, Sharpen, Edge Detection
- Grayscale, Sepia, Invert
- Emboss, Cartoon, Median

### Adjustments
- Brightness, Contrast, Saturation
- Live preview with sliders

### Transform
- Crop with preview
- Resize with aspect ratio
- Rotate (90°, -90°, 180°, free angle)
- Flip (horizontal/vertical)

### Drawing Tools
- Line, Rectangle, Circle
- Text with Persian/English support
- Custom colors and thickness
- Fill options

### Advanced Features
- Face Detection (face, eyes, smile)
- Face blur/pixelate
- Selection tool with operations
- Layers support
- Color Picker (RGB/HEX)
- Histogram display
- Before/After comparison
- Batch processing
- Image blending

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Build Executable

```bash
python build_exe.py
```

The executable will be created in the `dist` folder.

## Requirements

- Python 3.8+
- PyQt5
- OpenCV
- NumPy
- Pillow

## License

MIT License - See [LICENSE](LICENSE) file for details.

Copyright (c) 2024 [D-speedster](https://github.com/D-speedster)
