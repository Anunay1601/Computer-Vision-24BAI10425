# ScanSight: Automatic Document Scanner and Quality Analyzer

## Computer Vision Project Report

**Course:** Computer Vision
**Project Area:** Classical Digital Image Processing & Document Analysis

### Student Information

| Field                   | Details                                                |
| ----------------------- | ------------------------------------------------------ |
| **Name**                | Anunay Chhapre                                         |
| **Registration Number** | 24BAI10425                                             |
| **Course**              | Computer Vision                                        |
| **Project Area**        | Classical Digital Image Processing & Document Analysis |

---

# 1. Abstract

ScanSight is a computer vision-based document scanning and quality analysis system developed using classical digital image processing techniques.

The system takes a photograph containing a document as input and automatically identifies the document region, corrects perspective distortion, enhances the resulting document image, and evaluates its visual quality.

The project uses techniques such as grayscale conversion, Gaussian filtering, Canny edge detection, image dilation, contour detection, polygon approximation, four-point perspective transformation, denoising, CLAHE-based contrast enhancement, and adaptive thresholding.

In addition to generating a scanner-like document image, ScanSight calculates quality-related measurements such as brightness, contrast, sharpness, and skew. The results are saved as processed images and a structured JSON report.

The complete system is designed to be executable from the command line, making the implementation reproducible without depending on a GUI-based development environment.

---

# 2. Introduction

Digitizing physical documents using photographs is a common computer vision problem. Images captured using mobile phones or cameras often contain perspective distortion, uneven illumination, noise, blur, and skew.

A document that is photographed at an angle does not have the same rectangular appearance as a scanned document. Therefore, simply saving the original photograph may not produce a suitable digital copy.

ScanSight addresses this problem through a sequence of classical image-processing operations. The system identifies the document boundary, estimates its four corners, transforms it into a rectangular view, enhances the resulting image, and measures its quality.

The project demonstrates how fundamental computer vision concepts can be combined into a practical document-analysis application without requiring a deep learning model.

---

# 3. Problem Statement

When a document is captured using a camera, several problems can affect its quality:

* Perspective distortion due to camera angle
* Uneven lighting
* Low contrast
* Image noise
* Blur
* Skew
* Background interference
* Non-uniform document appearance

Manually correcting these problems for every document is inefficient.

Therefore, the objective of this project is to develop an automated computer vision pipeline that can:

1. Detect the document boundary.
2. Locate the document corners.
3. Correct perspective distortion.
4. Enhance the resulting document.
5. Measure document image quality.
6. Generate useful output reports.
7. Execute the complete workflow from the command line.

---

# 4. Objectives

The main objectives of ScanSight are:

* To implement a practical document-scanning system using classical computer vision.
* To detect document boundaries automatically.
* To identify the four corners of a document.
* To perform perspective correction.
* To improve document readability using image enhancement techniques.
* To estimate brightness, contrast, sharpness, and skew.
* To generate a structured quality report.
* To provide visual output for analyzing the processing pipeline.
* To make the project reproducible through command-line execution.

---

# 5. Scope of the Project

The project focuses on the processing and analysis of document photographs.

The scope includes:

* Input image processing
* Document boundary detection
* Edge detection
* Contour analysis
* Perspective transformation
* Image enhancement
* Quality measurement
* Report generation
* Command-line execution
* Automated testing

The project primarily focuses on documents whose boundaries can be reasonably detected from the image.

---

# 6. Proposed Solution

ScanSight uses a sequential image-processing pipeline.

The general workflow is:

```text
Input Image
     |
     v
Image Loading
     |
     v
Grayscale Conversion
     |
     v
Gaussian Blur
     |
     v
Canny Edge Detection
     |
     v
Dilation
     |
     v
Contour Detection
     |
     v
Polygon Approximation
     |
     v
Document Boundary Detection
     |
     v
Perspective Transformation
     |
     v
Scanned Document
     |
     v
Image Enhancement
     |
     +-----------------------+
     |                       |
     v                       v
Denoising             CLAHE Enhancement
     |                       |
     +-----------+-----------+
                 |
                 v
        Adaptive Thresholding
                 |
                 v
         Quality Analysis
                 |
                 +------------------+
                 |        |         |
                 v        v         v
             Brightness Contrast Sharpness
                 |
                 v
             Skew Analysis
                 |
                 v
        Output Images + JSON
```

---

# 7. Methodology

## 7.1 Image Loading

The input document photograph is first loaded using image-processing utilities.

The system supports common image formats such as:

* JPG
* JPEG
* PNG
* BMP

The image is then prepared for further processing.

---

## 7.2 Grayscale Conversion

The original image is converted from a color representation to grayscale.

Grayscale conversion reduces the image to a single intensity channel and simplifies subsequent edge and contour operations.

Instead of processing three color channels independently, the system can focus on intensity changes that are important for detecting document boundaries.

---

## 7.3 Gaussian Blur

A Gaussian filter is applied to reduce high-frequency noise.

This smoothing operation helps make edge detection more stable by reducing small unwanted variations in the image.

The filtered image is then used for subsequent edge detection.

---

## 7.4 Canny Edge Detection

Canny edge detection is used to identify strong intensity transitions.

The detected edges provide information about the boundaries of objects in the image.

For document scanning, the edges around the document are particularly important because they can be used to identify the document contour.

---

## 7.5 Dilation

Dilation is applied to strengthen and connect relevant edge regions.

This can help close small gaps between nearby edge pixels and make the document boundary easier to detect during contour extraction.

---

## 7.6 Contour Detection

Contours are extracted from the processed edge image.

A contour represents a continuous boundary around a region.

The system examines detected contours to identify a contour that is likely to correspond to the document.

---

## 7.7 Polygon Approximation

The detected contour is approximated using a polygon.

A document generally has a rectangular shape and therefore can be represented using four corner points.

Polygon approximation helps reduce a complex contour into a smaller number of meaningful points.

The four detected points represent the document corners.

---

# 8. Perspective Correction

A photograph of a document may be captured from an angle.

For example:

```text
Photographed Document

       _________
      /        /
     /        /
    /________/

          |
          | Perspective Transform
          v

Flattened Document

    ______________
   |              |
   |              |
   |              |
   |______________|
```

ScanSight uses the detected four document corners to perform a four-point perspective transformation.

The transformation maps the quadrilateral document region into a rectangular output.

This produces a scanner-like representation of the document.

---

# 9. Image Enhancement

After perspective correction, the document image is enhanced to improve readability.

## 9.1 Denoising

Denoising reduces unwanted image variations while attempting to preserve important document details.

This is useful when the input photograph contains sensor noise or small visual artifacts.

---

## 9.2 CLAHE Contrast Enhancement

CLAHE stands for **Contrast Limited Adaptive Histogram Equalization**.

It improves local contrast instead of applying the same contrast transformation to the entire image.

This is useful for document photographs where different regions may have different illumination levels.

---

## 9.3 Adaptive Thresholding

Adaptive thresholding converts the image into a form where foreground document content can be separated more clearly from the background.

Unlike a single global threshold, adaptive thresholding calculates threshold values based on local image regions.

This can improve document readability when illumination is not uniform.

---

# 10. Document Quality Analysis

A major component of ScanSight is the analysis of the processed document.

The project calculates several measurable properties.

## 10.1 Brightness

Brightness represents the general intensity level of the document image.

Very dark or excessively bright images may indicate poor capture conditions.

---

## 10.2 Contrast

Contrast represents the difference between lighter and darker regions.

Adequate contrast is important for separating document content from its background.

---

## 10.3 Sharpness

Sharpness provides an indication of the amount of fine detail present in the image.

A blurred photograph generally contains less high-frequency detail than a sharp document image.

Therefore, sharpness can be used as an indicator of image clarity.

---

## 10.4 Skew

Skew represents the angular deviation of document content from the expected horizontal or vertical orientation.

Estimating skew helps identify whether the resulting document is properly aligned.

---

# 11. System Architecture

The project is divided into multiple modules.

```text
                    +-------------------+
                    |     main.py       |
                    +---------+---------+
                              |
                              v
                    +-------------------+
                    |      cli.py       |
                    | Command Interface |
                    +---------+---------+
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
+----------------+   +----------------+   +----------------+
| preprocessing  |   |    scanner     |   |    quality     |
|                |   |                |   |                |
| Edge Detection |   | Contours       |   | Brightness     |
| Enhancement    |   | Polygon        |   | Contrast       |
| Filtering      |   | Perspective    |   | Sharpness      |
+----------------+   +----------------+   | Skew           |
                                          +-------+--------+
                                                  |
                                                  v
                                         +----------------+
                                         |    report.py   |
                                         | Visual + JSON  |
                                         +----------------+
```

---

# 12. Software Architecture

The project follows a modular structure.

```text
src/scansight/
│
├── cli.py
├── config.py
├── io_utils.py
├── preprocessing.py
├── scanner.py
├── quality.py
└── report.py
```

### `cli.py`

Provides command-line execution and handles user-provided input.

### `config.py`

Contains centralized configuration values and processing thresholds.

### `io_utils.py`

Handles image reading, writing, and resizing utilities.

### `preprocessing.py`

Contains image preprocessing, edge detection, and enhancement operations.

### `scanner.py`

Handles document contour detection and perspective correction.

### `quality.py`

Calculates document quality metrics and related feedback.

### `report.py`

Generates visual and JSON reports.

---

# 13. Project Structure

```text
Computer-Vision-24BAI10425/
│
├── docs/
│   ├── project_report.md
│   └── diagrams/
│
├── outputs/
│
├── samples/
│
├── scripts/
│   └── generate_sample.py
│
├── src/
│   └── scansight/
│       ├── cli.py
│       ├── config.py
│       ├── io_utils.py
│       ├── preprocessing.py
│       ├── scanner.py
│       ├── quality.py
│       └── report.py
│
├── tests/
│   └── test_scansight.py
│
├── .gitignore
├── main.py
├── pyproject.toml
├── requirements.txt
├── PROJECT_PROFILE.md
├── README.md
└── docs/project_report.md
```

---

# 14. Technologies and Libraries

## Programming Language

**Python 3.10+**

Python was selected because of its extensive ecosystem for image processing and computer vision.

## OpenCV

OpenCV is used for the main computer vision operations, including:

* Image processing
* Gaussian filtering
* Canny edge detection
* Contour detection
* Polygon approximation
* Perspective transformation
* Image enhancement

## NumPy

NumPy is used for numerical and array-based image operations.

## Pillow

Pillow provides additional image handling capabilities.

## unittest

Python's built-in `unittest` framework is used for automated testing of core project functionality.

---

# 15. Command-Line Execution

The project is designed to be executed through the terminal.

## Installation

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

---

## Run the Project

The complete project can be started using:

```bash
python main.py
```

The project also provides a command-line demonstration:

```bash
python main.py --cli
```

To process a specific image:

```bash
python main.py --cli --input path/to/document.jpg
```

---

# 16. Testing

Automated tests are included in the project.

Run the test suite using:

```bash
python -m unittest discover -s tests
```

The test suite is intended to verify the functionality of the core computer vision components.

---

# 17. Output

After processing an image, ScanSight generates output files.

### 17.1 Scanned Document

```text
outputs/scanned_document.png
```

This contains the perspective-corrected and enhanced document.

### 17.2 Visual Report

```text
outputs/visual_report.png
```

This provides a visual representation of the processing pipeline and analysis.

### 17.3 Quality Report

```text
outputs/quality_report.json
```

This contains structured quality measurements.

Typical measurements include:

```text
Brightness
Contrast
Sharpness
Skew
```

---

# 18. Results and Discussion

The implemented pipeline demonstrates that a document can be processed using a sequence of classical computer vision operations.

The system is able to:

* Identify prominent document boundaries.
* Estimate document corners using contour processing.
* Transform a perspective-distorted document into a rectangular view.
* Improve document appearance using enhancement techniques.
* Produce measurable quality information.
* Save the results in reusable image and JSON formats.

The quality of document detection depends on factors such as document visibility, background complexity, illumination, image resolution, and the strength of the document boundary.

The system therefore provides both the processed document and measurable quality information instead of relying only on visual inspection.

---

# 19. Advantages

The proposed system provides several advantages:

1. **Classical Computer Vision Approach**
   The project demonstrates fundamental image-processing concepts without requiring model training.

2. **No Training Dataset Required**
   The document detection pipeline is based on image-processing operations rather than a trained neural network.

3. **Modular Architecture**
   Different processing components are separated into individual modules.

4. **Command-Line Execution**
   The project can be executed from a terminal environment.

5. **Quality Measurement**
   The system produces measurable image-quality information.

6. **Structured Output**
   Results are available as images and JSON data.

7. **Easy Extension**
   Additional enhancement methods, quality metrics, or document-detection approaches can be added to the modular architecture.

---

# 20. Limitations

The current implementation has some limitations.

### Document Boundary Dependence

The system works best when the document has a clearly visible boundary.

### Complex Backgrounds

Backgrounds with many strong edges may make document contour detection more difficult.

### Poor Lighting

Extremely uneven lighting can affect edge detection and thresholding.

### Severe Blur

Heavy motion blur or out-of-focus images can reduce the quality of detected contours.

### Occlusion

If a large part of the document is hidden, the four document corners may not be detected reliably.

### Irregular Documents

The current approach is primarily designed around documents that can be represented using a four-corner boundary.

---

# 21. Future Scope

The project can be extended in several ways.

## OCR Integration

An OCR system could be added to extract text from the processed document.

## Automatic Document Classification

Different document types such as invoices, forms, certificates, and identity documents could be classified automatically.

## Deep Learning-Based Detection

A trained object-detection or segmentation model could be added for more difficult document-background conditions.

## Advanced Quality Assessment

Additional metrics could be introduced for:

* Illumination uniformity
* Text readability
* Blur estimation
* Noise level
* Document completeness

## Mobile Deployment

The processing pipeline could be adapted for a mobile document-scanning application.

## Batch Processing

The system could be extended to process multiple documents automatically.

---

# 22. Applications

ScanSight's techniques can be applied to:

* Digital document scanning
* OCR preprocessing
* Document digitization
* Document archival
* Automated document workflows
* Mobile scanning applications
* Document quality assessment
* Educational demonstrations of computer vision

---

# 23. Conclusion

ScanSight demonstrates the practical application of classical digital image processing techniques to the problem of document scanning and analysis.

The system combines preprocessing, edge detection, contour analysis, polygon approximation, perspective transformation, image enhancement, and quality measurement into a complete pipeline.

The project provides a practical example of how fundamental computer vision techniques can be combined to solve a real-world image-processing problem.

The modular implementation, command-line execution, automated tests, visual outputs, and JSON quality report make the system suitable for experimentation, evaluation, and further development.

---

# 24. References

1. OpenCV Documentation — Image Processing and Computer Vision.
2. Rafael C. Gonzalez and Richard E. Woods, *Digital Image Processing*.
3. Richard Szeliski, *Computer Vision: Algorithms and Applications*.
4. OpenCV documentation on Canny Edge Detection.
5. OpenCV documentation on Contour Detection.
6. OpenCV documentation on Perspective Transformation.
7. OpenCV documentation on CLAHE and image enhancement.

---

# 25. Author

**Anunay Chhapre**

**Registration Number:** 24BAI10425

**Course:** Computer Vision

**Project Area:** Classical Digital Image Processing & Document Analysis

**Repository:**
https://github.com/Anunay1601/Computer-Vision-24BAI10425

