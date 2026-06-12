import os
import asyncio
import openai
from PySide6.QtCore import QObject, Signal
from core.excel import parse_excel, write_excel
from core.ai import analyze_boq_stream
from core import db

class WorkerSignals(QObject):
    log = Signal(str)
    finished = Signal(str)
    error = Signal(str)

def check_connection(api_key: str, base_url: str, model_id: str) -> bool:
    try:
        client = openai.OpenAI(api_key=api_key, base_url=base_url)
        client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5
        )
        return True
    except Exception as e:
        print(f"Connection check failed: {e}")
        return False

def run_analysis(api_key: str, base_url: str, model_id: str, system_prompt: str, user_prompt: str, signals: WorkerSignals) -> dict:
    gen = analyze_boq_stream(
        api_key=api_key,
        base_url=base_url,
        model_id=model_id,
        system_prompt=system_prompt,
        user_prompt=user_prompt
    )
    last_was_thought = None
    try:
        for token, is_thought in gen:
            if is_thought:
                if last_was_thought != True:
                    signals.log.emit("\n[Thinking] ")
                    last_was_thought = True
                signals.log.emit(token)
            else:
                if last_was_thought == True:
                    signals.log.emit("\n")
                last_was_thought = False
                signals.log.emit(token)
    except StopIteration as e:
        return e.value
    raise RuntimeError("AI analysis finished unexpectedly without returning parsed data.")

class BOQProcessor:
    def __init__(self, file_path: str, signals: WorkerSignals):
        self.file_path = file_path
        self.signals = signals
        self.settings = db.get_settings()
        
    async def process(self):
        try:
            self.signals.log.emit("Parsing Excel BOQ file...")
            markdown_content, data_mapping, headers_mapping = await asyncio.to_thread(
                parse_excel, self.file_path
            )
            self.signals.log.emit(f"Successfully parsed {len(data_mapping)} items from Excel.")
            
            api_key = self.settings.get('api_key', '')
            model_id = self.settings.get('model_id', 'MiniMax-M3')
            base_url = self.settings.get('base_url', 'https://api.minimax.io/v1')
            
            if not api_key:
                raise ValueError("API Key is missing. Please configure it in Settings.")
                
            self.signals.log.emit(f"Sending request to AI Model ({model_id})...")
            
            system_prompt = (
                "You are an expert Quantity Surveyor and Construction Estimator.\n"
                "Your task is to analyze the Bill of Quantities (BOQ) items provided in Markdown format, "
                "and categorize each item (using its Global ID, e.g., 'R1', 'R2') "
                "into a MACRO-LEVEL Work Package (e.g., Concrete Works, Masonry, HVAC, Plumbing, Electrical, Finishes).\n"
                "DO NOT use granular item names as packages. Group related items into high-level trades.\n"
                "You must return a JSON object with the following structure:\n"
                "{\n"
                "  \"project_name\": \"Name of the project or default name\",\n"
                "  \"date\": \"YYYY-MM-DD or default current date\",\n"
                "  \"items\": {\n"
                "    \"R1\": \"Work Package Name\",\n"
                "    \"R2\": \"Work Package Name\"\n"
                "  }\n"
                "}\n"
                "Output ONLY valid JSON. Do not write anything other than the JSON object."
            )
            
            user_prompt = f"Analyze and categorize these BOQ items:\n\n{markdown_content}"
            
            parsed_data = await asyncio.to_thread(
                run_analysis, api_key, base_url, model_id, system_prompt, user_prompt, self.signals
            )
            
            project_name = parsed_data.get("project_name", "Tawreed Project")
            date = parsed_data.get("date", "")
            item_categories = parsed_data.get("items", {})
            
            self.signals.log.emit(f"\nAI identified project: {project_name}")
            self.signals.log.emit(f"Categorized {len(item_categories)} items into work packages.")
            
            output_dir = db.get_outputs_dir()
            base_name = os.path.basename(self.file_path)
            name_without_ext, _ = os.path.splitext(base_name)
            output_file = os.path.join(output_dir, f"{name_without_ext}_Tawreed_Output.xlsx")
            
            self.signals.log.emit(f"Generating output workbook: {output_file}")
            
            await asyncio.to_thread(
                write_excel, output_file, data_mapping, item_categories, project_name, date
            )
            
            await asyncio.to_thread(
                db.add_history, project_name, len(set(item_categories.values())), output_file
            )
            
            self.signals.finished.emit(output_file)
            
        except Exception as e:
            self.signals.error.emit(str(e))
