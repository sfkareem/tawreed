import os
import webview
import json
import logging
import traceback
import sys
from tawreed_backend import (
    load_config,
    save_config,
    JobProcessor,
    AIService,
    CONFIG_DIR,
    LOG_DIR
)

logger = logging.getLogger("TawreedMain")

class TawreedAPI:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def select_file(self) -> str:
        """Opens a file dialog to select a BOQ or procurement document."""
        if not self._window:
            return ""
        
        file_types = (
            "Project Files (*.xlsx;*.xls;*.xlsm;*.csv;*.docx;*.pdf;*.png;*.jpg;*.jpeg)",
            "Excel Files (*.xlsx;*.xls;*.xlsm)",
            "CSV Files (*.csv)",
            "Word Files (*.docx)",
            "PDF Files (*.pdf)",
            "Images (*.png;*.jpg;*.jpeg)",
            "All Files (*.*)"
        )
        
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=file_types
        )
        
        if result and len(result) > 0:
            return result[0]
        return ""

    def select_output_folder(self) -> str:
        """Opens a directory selection dialog."""
        if not self._window:
            return ""
        
        result = self._window.create_file_dialog(
            webview.FOLDER_DIALOG
        )
        
        if result and len(result) > 0:
            return result[0]
        return ""

    def load_settings(self) -> dict:
        """Reads configuration settings."""
        return load_config()

    def save_settings(self, settings: dict) -> bool:
        """Saves configuration settings."""
        return save_config(settings)

    def test_connection(self, settings: dict) -> dict:
        """Tests connection to the configured AI API."""
        test_prompt = (
            "You are a test agent. Respond with a raw JSON object containing exactly "
            "one field: 'status' with the value 'success'. Do not output markdown."
        )
        
        raw_res, err = AIService.call_ai(settings, test_prompt)
        if err:
            return {"status": "error", "message": err}
        
        try:
            # Clean and load JSON
            import re
            cleaned_str = raw_res.strip()
            match = re.search(r"(\{.*?\})", cleaned_str, re.DOTALL)
            if match:
                cleaned_str = match.group(1)
            
            data = json.loads(cleaned_str)
            if data.get("status") == "success" or data.get("status") == "ok":
                return {"status": "success", "message": "Connection test passed successfully!"}
            else:
                return {"status": "error", "message": f"Unexpected response content: {raw_res}"}
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Connection test failed to parse response JSON: {str(e)}. Raw: {raw_res}"
            }

    def generate(self, file_path: str, output_dir: str, language: str) -> dict:
        """Runs the material extraction job."""
        if not file_path or not os.path.exists(file_path):
            return {"status": "error", "message": "Selected input file does not exist."}
        
        if not output_dir:
            output_dir = CONFIG_DIR
            
        if not os.path.exists(output_dir):
            return {"status": "error", "message": "Selected output folder does not exist."}
        
        config = load_config()
        try:
            manifest = JobProcessor.run(file_path, output_dir, config, language)
            return {"status": "success", "data": manifest}
        except Exception as e:
            logger.error(f"Job generation error: {e}\n{traceback.format_exc()}")
            return {"status": "error", "message": str(e)}

    def get_jobs_history(self) -> list:
        """Retrieves history of past jobs based on manifest files."""
        history = []
        try:
            if os.path.exists(LOG_DIR):
                for folder in os.listdir(LOG_DIR):
                    folder_path = os.path.join(LOG_DIR, folder)
                    if os.path.isdir(folder_path):
                        manifest_path = os.path.join(folder_path, "manifest.json")
                        if os.path.exists(manifest_path):
                            with open(manifest_path, "r", encoding="utf-8") as f:
                                manifest = json.load(f)
                                history.append(manifest)
            # Sort by timestamp descending
            history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        except Exception as e:
            logger.error(f"Error loading job history: {e}")
        return history

    def get_diagnostics(self, job_id: str) -> dict:
        """Retrieves raw telemetry data for a specific job."""
        job_log_dir = os.path.join(LOG_DIR, job_id)
        if not os.path.exists(job_log_dir):
            return {"status": "error", "message": "Job diagnostics folder not found."}
            
        diag = {
            "serialized_input": "",
            "system_prompt": "",
            "raw_ai_response": "",
            "extracted_data": "",
            "repair_attempt": "",
            "error": ""
        }
        
        for k in diag.keys():
            file_path = os.path.join(job_log_dir, f"{k}.txt" if k != "extracted_data" and k != "repair_attempt" and k != "error" else f"{k}.json" if k == "extracted_data" else f"{k}.log")
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        diag[k] = f.read()
                except Exception as e:
                    diag[k] = f"[Error reading file: {str(e)}]"
        return {"status": "success", "diagnostics": diag}

    def open_folder(self, path: str) -> bool:
        """Opens a directory in Windows Explorer."""
        if not path or not os.path.exists(path):
            return False
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", path])
            else: # linux
                import subprocess
                subprocess.Popen(["xdg-open", path])
            return True
        except Exception as e:
            logger.error(f"Failed to open folder {path}: {e}")
            return False

def main():
    api = TawreedAPI()
    
    # Path to GUI index.html
    gui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gui")
    index_html = os.path.join(gui_dir, "index.html")
    
    if not os.path.exists(index_html):
        # Fallback for development if gui directory structure is being built
        logger.warning(f"Index.html not found at {index_html}. Starting with simple fallback html.")
        os.makedirs(gui_dir, exist_ok=True)
        # Create a simple placeholder until actual GUI is loaded
        with open(index_html, "w", encoding="utf-8") as f:
            f.write("<html><body><h1>Loading Tawreed Interface...</h1></body></html>")

    # Start PyWebView
    logger.info("Initializing pywebview window...")
    window = webview.create_window(
        title="Tawreed - Construction Materials Extractor",
        url=index_html,
        js_api=api,
        width=1100,
        height=750,
        min_size=(900, 600),
        background_color="#1E1E2F"
    )
    api.set_window(window)
    webview.start(debug=False)

if __name__ == "__main__":
    main()
