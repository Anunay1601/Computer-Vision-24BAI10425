# DocuVision — Automatic Document Scanner & Quality Analyzer

### Computer Vision Project

**Project Area:** Classical Digital Image Processing & Document Analysis

---

## 👨‍🎓 Student Information

| Field                   | Details                                                |
| ----------------------- | ------------------------------------------------------ |
| **Name**                | Anunay Chhapre                                         |
| **Registration Number** | 24BAI10425                                             |
| **Course**              | Computer Vision                                        |
| **Project Area**        | Classical Digital Image Processing & Document Analysis |

---

## 📌 Project Overview

**DocuVision** is a computer vision-based document scanning and quality analysis system.

The project takes a photograph of a document, automatically detects the document boundary, corrects perspective distortion, enhances the scanned result, and evaluates the quality of the resulting document.

The project focuses on **classical digital image processing and document analysis techniques** rather than deep-learning-based document detection.

The complete project can be installed and executed from the **command line**, making it suitable for terminal-based evaluation.

---

## ✨ Features

### 1. Automatic Document Detection

The system detects the document boundary using classical computer vision techniques:

* Grayscale conversion
* Gaussian blur
* Canny edge detection
* Image dilation
* Contour extraction
* Polygon approximation

### 2. Perspective Correction

The detected document corners are used to perform a **four-point perspective transformation**.

This converts a photographed document into a flattened, scanner-like view.

### 3. Document Enhancement

The scanned document is enhanced using:

* Denoising
* CLAHE-based contrast enhancement
* Adaptive thresholding

These operations improve the readability of the document.

### 4. Document Quality Analysis

DocuVision calculates measurable image-quality properties including:

* Brightness
* Contrast
* Sharpness
* Skew

### 5. Automated Reports

The system generates:

* Processed/scanned document
* Visual processing report
* JSON quality report

---

# 🧠 Computer Vision Pipeline

```text
                    Input Document Image
                              │
                              ▼
                       Image Loading
                              │
                              ▼
                     Grayscale Conversion
                              │
                              ▼
                       Gaussian Blur
                              │
                              ▼
                     Canny Edge Detection
                              │
                              ▼
                           Dilation
                              │
                              ▼
                     Contour Detection
                              │
                              ▼
                    Polygon Approximation
                              │
                              ▼
                   Document Boundary Found
                              │
                              ▼
              Four-Point Perspective Transform
                              │
                              ▼
                    Scanned Document
                              │
                              ▼
                     Image Enhancement
                    ┌─────────┼─────────┐
                    │         │         │
                    ▼         ▼         ▼
                Denoising   CLAHE   Adaptive
                           Contrast  Thresholding
                    │         │         │
                    └─────────┼─────────┘
                              ▼
                       Quality Analysis
                    ┌─────────┼─────────┐
                    │         │         │
                    ▼         ▼         ▼
                Brightness Contrast Sharpness
                              │
                              ▼
                         Skew Analysis
                              │
                              ▼
                    Output + JSON Report
```

---

# 🛠️ Technologies Used

* **Python 3.10+**
* **OpenCV**
* **NumPy**
* **Pillow**
* **Python unittest**
* **Mermaid** for documentation diagrams

---

# 📂 Project Structure

```text
Computer-Vision-24BAI10425/
│
├── docs/
│   ├── project_report.md
│   └── diagrams/
│
├── outputs/
│   ├── scanned_document.png
│   ├── visual_report.png
│   └── quality_report.json
│
├── samples/
│
├── scripts/
│   └── generate_sample.py
│
├── src/
│   └── docuvision/
│       ├── cli.py
│       ├── config.py
│       ├── io_utils.py
│       ├── preprocessing.py
│       ├── scanner.py
│       ├── quality.py
│       └── report.py
│
├── tests/
│   └── test_docuvision.py
│
├── .gitignore
├── main.py
├── pyproject.toml
├── requirements.txt
├── PROJECT_PROFILE.md
├── BuildYourOwnProjectVITyarthi.pdf
└── README.md
```

---

# ⚙️ Installation & Setup

The project can be completely configured from the terminal.

## Step 1 — Clone the Repository

```bash
git clone https://github.com/Anunay1601/Computer-Vision-24BAI10425.git
```

Navigate to the project directory:

```bash
cd Computer-Vision-24BAI10425
```

---

## Step 2 — Check Python Version

Python **3.10 or newer** is recommended.

Check your installed Python version:

```bash
python --version
```

If your system uses `python3`, run:

```bash
python3 --version
```

---

## Step 3 — Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
```

Activate the environment using PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Alternatively, from Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

After activation, the terminal should display:

```text
(.venv)
```

---

## Step 4 — Install Dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the required Python packages:

```bash
python -m pip install -r requirements.txt
```

Install the project package in editable mode:

```bash
python -m pip install -e .
```

---

# ▶️ Running the Project

## Command-Line Execution

The project provides a command-line interface and can be executed without requiring a GUI-based development environment.

### Run the Demo

```bash
python main.py --cli
```

This runs the complete document-processing pipeline using the available sample/demo input.

---

## Process Your Own Document

To process a document image from the terminal:

```bash
python main.py --cli --input path/to/document.jpg
```

Example:

```bash
python main.py --cli --input samples/document.jpg
```

Common supported image formats include:

* JPG
* JPEG
* PNG
* BMP

---

# 📊 Generated Outputs

After successful execution, the processed results are available in the `outputs/` directory.

### Scanned Document

```text
outputs/scanned_document.png
```

Contains the perspective-corrected and enhanced document.

### Visual Report

```text
outputs/visual_report.png
```

Contains a visual representation of the processing and quality analysis.

### Quality Report

```text
outputs/quality_report.json
```

Contains machine-readable document quality measurements.

The report includes metrics such as:

```text
Brightness
Contrast
Sharpness
Skew
```

The exact values depend on the input image.

---

# 🧪 Testing

The project includes automated unit tests for the core computer vision functionality.

Run all tests from the project root:

```bash
python -m unittest discover -s tests
```

A successful test run indicates that the implemented core processing components are functioning correctly.

---

# 🔬 Methodology

## 1. Image Preprocessing

The input image is prepared for further analysis through grayscale conversion and smoothing.

## 2. Edge Detection

Canny edge detection is used to identify significant boundaries in the image.

## 3. Contour Detection

Contours are extracted from the edge image to identify possible document boundaries.

## 4. Polygon Approximation

Detected contours are approximated as polygons to identify a possible four-corner document.

## 5. Perspective Transformation

The four detected document corners are used to perform a perspective transformation.

This produces a top-down rectangular representation of the document.

## 6. Image Enhancement

The scanned document is enhanced through:

* Denoising
* CLAHE contrast enhancement
* Adaptive thresholding

## 7. Quality Analysis

The processed document is evaluated using:

* Brightness
* Contrast
* Sharpness
* Skew estimation

## 8. Report Generation

The final scanned image, visual report, and quality measurements are saved to the `outputs/` directory.

---

# 🎯 Project Objectives

The objectives of DocuVision are:

* Apply classical computer vision techniques to a practical document-processing problem.
* Automatically identify document boundaries.
* Correct perspective distortion in photographed documents.
* Improve document readability.
* Measure document image quality using objective metrics.
* Generate structured processing results.
* Provide complete command-line execution.
* Demonstrate practical applications of digital image processing.

---

# 💡 Applications

The techniques implemented in DocuVision can be applied to:

* Digital document scanning
* Document digitization
* OCR preprocessing
* Document quality assessment
* Mobile document-scanning applications
* Digital archiving
* Automated document-processing systems

---

# ⚠️ Limitations

The performance of the system may decrease when:

* The document boundary is not clearly visible.
* The image contains heavy background clutter.
* The document is severely blurred.
* Lighting is extremely uneven.
* Large portions of the document are occluded.
* The document has an irregular or damaged boundary.
* The input image has very low resolution.

The current implementation uses classical image-processing methods and does not use a trained deep-learning document detector.

---

# 📚 References

1. OpenCV Documentation — Image Processing, Edge Detection, Contours and Perspective Transformation.
2. Rafael C. Gonzalez and Richard E. Woods, *Digital Image Processing*.
3. Richard Szeliski, *Computer Vision: Algorithms and Applications*.

---

# 👨‍💻 Author

**Anunay Chhapre**

**Registration Number:** 24BAI10425

**Course:** Computer Vision

**Project Area:** Classical Digital Image Processing & Document Analysis

---

## 🎓 Academic Project

This project was developed as part of the **Computer Vision** course to demonstrate the practical application of classical digital image processing and document-analysis techniques.

The project is designed to be reproducible and executable through the command line after following the installation instructions provided above.
