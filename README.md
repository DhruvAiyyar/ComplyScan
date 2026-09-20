# ComplyScan 🔍

> **AI-powered Legal Metrology Compliance Scanner for Packaged Commodities**

ComplyScan is an AI-powered compliance assistance platform designed to simplify the inspection of packaged commodities under India's **Legal Metrology (Packaged Commodities) Rules**.

The platform uses **OCR, computer vision, automated rule validation, and a web-based dashboard** to extract mandatory declarations from product labels and identify potential compliance issues.

<p align="center">
  <a href="https://complyscan-seven.vercel.app/">
    <strong>🚀 Live Demo</strong>
  </a>
</p>

---

## 📌 Problem

Inspection of packaged commodities often requires manually checking multiple declarations on product packaging, including:

* Manufacturer / Packer / Importer details
* Product name
* Net quantity
* Maximum Retail Price (MRP)
* Date of manufacture / packing / import
* Consumer care information
* Country of origin
* Other mandatory declarations

Manual verification can be time-consuming and may result in inconsistent documentation.

**ComplyScan aims to make this process faster, structured, and technology-assisted.**

---

## 💡 Solution

ComplyScan converts a product label image into a structured compliance analysis.

```text
Product / Label Image
        ↓
Image Processing
        ↓
OCR & Text Extraction
        ↓
Information Extraction
        ↓
Compliance Rule Validation
        ↓
Potential Issues / Findings
        ↓
Compliance Report
```

The system is designed to assist inspectors by reducing repetitive manual work while keeping the final decision with the authorized human reviewer.

---

## ✨ Key Features

### 📷 AI-Powered Product Scanning

Upload an image of a packaged commodity and let ComplyScan analyze the visible label information.

### 🔤 OCR-Based Text Extraction

Automatically extract relevant text from product packaging instead of requiring manual data entry.

### 📋 Structured Declaration Extraction

Identify and organize important declarations such as:

* Product name
* Manufacturer / Packer / Importer
* Address
* Net quantity
* MRP
* Manufacturing / Packing / Import date
* Consumer care details
* Country of origin

### ⚖️ Compliance Verification

Compare extracted information against configured compliance requirements and identify potential issues.

### 🚨 Issue Detection

The system can highlight situations such as:

* Missing mandatory declarations
* Incomplete information
* Potentially inconsistent information
* Conflicting information between package images
* Low-confidence OCR results requiring manual verification

### 📊 Inspector Dashboard

A simple web interface allows users to:

* Upload product images
* Run compliance scans
* View extracted information
* Review compliance findings
* Examine supporting evidence
* Track inspection-related information

---

## 🏗️ Architecture

```text
                     ┌───────────────────────┐
                     │      Frontend         │
                     │    Inspector UI       │
                     └───────────┬───────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │       Backend         │
                     │       REST API        │
                     └───────────┬───────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
       │    Image    │    │     OCR     │    │    Rule     │
       │ Processing  │    │  Pipeline   │    │   Engine    │
       └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 ▼
                     ┌───────────────────────┐
                     │ Compliance Analysis   │
                     └───────────┬───────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │ Results & Evidence    │
                     └───────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend

* React
* JavaScript / TypeScript
* Responsive web interface
* Vercel

### Backend

* Python
* REST APIs
* Compliance processing services

### AI / Computer Vision

* Optical Character Recognition (OCR)
* Computer Vision
* Image preprocessing
* AI-assisted information extraction

### Development & Deployment

* Git
* GitHub
* Vercel
* API-based architecture

---

## 📂 Project Structure

```text
ComplyScan/
│
├── frontend/
│   └── Frontend application
│
├── backend/
│   └── Backend APIs and processing
│
├── data/
│   └── Application / sample data
│
├── docs/
│   └── Project documentation
│
├── vercel.json
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed:

* [Node.js](https://nodejs.org/)
* npm
* Python 3.x
* Git

---

### 1. Clone the Repository

```bash
git clone https://github.com/DhruvAiyyar/ComplyScan.git
cd ComplyScan
```

---

### 2. Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment.

**macOS / Linux**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
python app.py
```

> The exact startup command may vary depending on the configured backend entry point.

---

### 3. Frontend Setup

Open a new terminal and navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The terminal will display the local URL for the frontend.

---

## 🌐 Live Demo

**Live Prototype:**
https://complyscan-seven.vercel.app/

---

## 🔎 How It Works

### 1. Upload

The inspector uploads an image of a packaged commodity or product label.

### 2. Image Processing

The uploaded image is prepared for analysis to improve text recognition.

### 3. OCR

The system extracts visible text from the product packaging.

### 4. Information Extraction

Relevant compliance-related information is identified and converted into structured fields.

### 5. Rule Validation

The extracted information is evaluated against the configured compliance requirements.

### 6. Results

The system presents the inspection results, including detected information and potential compliance issues.

---

## 🎯 Use Cases

ComplyScan can be used as a technology-assisted workflow for:

* Legal Metrology inspections
* Preliminary product compliance checks
* Packaged commodity verification
* Digital inspection workflows
* Compliance documentation
* Regulatory technology research
* Academic and hackathon prototypes

---

## 🔐 Human-in-the-Loop Approach

ComplyScan is designed as a **decision-support system**, not an autonomous enforcement system.

AI-generated results may contain errors due to:

* Image quality
* Packaging design
* Occlusion
* Font variations
* OCR limitations
* Ambiguous declarations

Therefore, potential violations and low-confidence results should be reviewed by an authorized inspector before any regulatory action is taken.

---

## 🚧 Current Limitations

As a prototype, ComplyScan may have limitations related to:

* Image quality and lighting
* Complex packaging layouts
* Curved or distorted surfaces
* Handwritten or stylized text
* Multilingual labels
* OCR accuracy
* Changes in regulatory requirements

The platform should therefore be treated as an **inspection assistance tool**, rather than a replacement for official regulatory verification.

---

## 🗺️ Roadmap

### Current

* [x] Product image upload
* [x] Web-based scanning interface
* [x] OCR-based text extraction
* [x] Declaration extraction
* [x] Compliance analysis workflow
* [x] Frontend and backend architecture
* [x] Prototype deployment

### Future

* [ ] Multilingual OCR
* [ ] Improved image preprocessing
* [ ] Better handling of curved packaging
* [ ] Advanced violation detection
* [ ] Automated compliance reports
* [ ] Historical inspection analytics
* [ ] Inspector authentication
* [ ] Role-based access control
* [ ] Advanced evidence visualization
* [ ] Real-world benchmark datasets
* [ ] Integration with authoritative regulatory data
* [ ] Mobile application for field inspectors

---

## 📈 Future Vision

The long-term vision for ComplyScan is to develop a complete digital compliance-assistance ecosystem.

```text
        Product Scanning
               ↓
        AI / OCR Extraction
               ↓
     Regulatory Knowledge Base
               ↓
       Automated Validation
               ↓
       Evidence & Risk Analysis
               ↓
          Inspector Review
               ↓
      Digital Inspection Report
               ↓
       Analytics & Monitoring
```

This could help transform traditional inspection workflows into a more **digital, structured, transparent, and data-driven process**.

---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

### Fork the repository

```bash
git clone https://github.com/DhruvAiyyar/ComplyScan.git
```

### Create a feature branch

```bash
git checkout -b feature/your-feature
```

### Commit your changes

```bash
git add .
git commit -m "Add: your feature"
```

### Push the branch

```bash
git push origin feature/your-feature
```

Then open a Pull Request.

---

## ⚠️ Disclaimer

ComplyScan is a **prototype developed for demonstration, research, and educational purposes**.

It does not constitute legal advice, official regulatory certification, or a replacement for inspection by authorized authorities.

Compliance decisions should always be based on the latest applicable laws, rules, notifications, amendments, and official regulatory guidance.

---

## 👨‍💻 Project

**ComplyScan**

AI-powered Legal Metrology Compliance Scanner for Packaged Commodities.

Built with ❤️ using AI, OCR, Computer Vision, and modern web technologies.

---

<p align="center">
  <strong>ComplyScan — Scan. Analyze. Verify. Comply.</strong>
</p>
