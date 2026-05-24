# Tawreed (توريد) 🏗️

Tawreed is a modern, AI-powered desktop application designed to streamline the extraction and processing of materials from construction **Bills of Quantities (BOQs)** and procurement documents. By integrating advanced LLM capabilities with a sleek, native-feeling web interface, Tawreed converts complex, unstructured documents into clean, structured Excel sheets for estimation and supply chain workflows.

---

## ✨ Features

- **Multi-Format Document Ingestion**: Seamlessly ingest BOQ documents in diverse formats including:
  - Excel Sheets (`.xlsx`, `.xls`, `.xlsm`)
  - Word Documents (`.docx`)
  - PDFs (`.pdf`)
  - CSV files (`.csv`)
  - Scanned sheets and screenshots (`.png`, `.jpg`, `.jpeg`)
- **AI-Powered Material Extraction**: Leverages configurable Large Language Models (LLMs) to automatically detect, normalize, and extract materials, quantities, units, and structural descriptions.
- **Sleek, Modern Web UI**: Premium desktop dashboard powered by PyWebView, CSS Glassmorphism, and responsive modern layouts.
- **Detailed Diagnostics & Telemetry**: Full execution history tracking with logs showing system prompts, raw LLM responses, data normalizations, and automatic repair steps.
- **Customizable LLM Configuration**: In-app setup to configure API providers, model parameters, system instructions, and target output schemas.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+
- **Frontend**: HTML5, Vanilla CSS (Glassmorphism & dark theme), Javascript
- **Desktop Wrapper**: [PyWebView](https://pywebview.flowrl.com/)
- **Data Engineering**: Pandas, OpenPyXL, Python-Docx, PyPDF2
- **AI Integration**: Custom OpenAI-compatible REST API wrapper

---

## 🚀 Getting Started

### Prerequisites

Make sure you have Python 3.10 or higher installed.

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sfkareem/tawreed.git
   cd tawreed
   ```

2. **Set up a Virtual Environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # On Windows
   source .venv/bin/activate  # On macOS/Linux
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

To launch the desktop application in developer mode:
```bash
python main.py
```

---

## 📦 Building from Source (PyInstaller)

To bundle the application into a standalone executable (`.exe` on Windows):

1. Make sure PyInstaller is installed:
   ```bash
   pip install pyinstaller
   ```

2. Run the PyInstaller build:
   ```bash
   pyinstaller main.spec
   ```

The compiled standalone executable will be generated inside the `dist/Tawreed.exe` directory.

---

## 📄 License

This project is proprietary and confidential. All rights reserved.
