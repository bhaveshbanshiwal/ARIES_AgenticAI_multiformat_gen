import os
import json
import matplotlib.pyplot as plt
from typing import Any, List, Dict
from pptx import Presentation
from pptx.util import Inches
from docx import Document
from docx.shared import Inches as DocxInches
from langchain_core.tools import tool

# Explicitly use the Docker volume path
OUTPUT_DIR = "/app/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@tool
def generate_chart(title: str, labels: List[str], values: List[float], chart_type: str = "bar") -> str:
    """
    Generates a chart (bar or pie) and saves it as an image.
    Returns the file path of the generated chart.
    """
    plt.figure(figsize=(6, 4))
    if chart_type == "pie":
        plt.pie(values, labels=labels, autopct='%1.1f%%')
    else:
        plt.bar(labels, values)
    
    plt.title(title)
    plt.tight_layout()
    
    filename = f"{title.replace(' ', '_').lower()}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath)
    plt.close()
    
    return filepath

@tool
def create_pptx(filename: str, slides_data: str) -> str:
    """
    Generates a PPTX presentation.
    slides_data must be a JSON string representing a list of dictionaries:
    [{"title": "Slide 1", "bullets": ["Point 1", "Point 2"], "image_path": "optional/path.png"}]
    """
    try:
        data = json.loads(slides_data)
        prs = Presentation()
        
        for slide_info in data:
            slide_layout = prs.slide_layouts[1] 
            slide = prs.slides.add_slide(slide_layout)
            
            title_shape = slide.shapes.title
            body_shape = slide.placeholders[1]
            
            title_shape.text = slide_info.get("title", "")
            tf = body_shape.text_frame
            
            for bullet in slide_info.get("bullets", []):
                p = tf.add_paragraph()
                p.text = bullet
                
            if "image_path" in slide_info and os.path.exists(slide_info["image_path"]):
                slide.shapes.add_picture(slide_info["image_path"], Inches(5), Inches(2), width=Inches(4))
                
        filepath = os.path.join(OUTPUT_DIR, filename)
        prs.save(filepath)
        return f"Successfully created PPTX at: {filepath}"
    except Exception as e:
        return f"Error creating PPTX: {str(e)}"

@tool
def create_docx(filename: str, title: str, sections_data: str) -> str:
    """
    Generates a DOCX report.
    sections_data must be a JSON string representing a list of dictionaries:
    [{"heading": "Section 1", "content": "Paragraph text", "image_path": "optional/path.png"}]
    """
    try:
        data = json.loads(sections_data)
        doc = Document()
        doc.add_heading(title, 0)
        
        for section in data:
            doc.add_heading(section.get("heading", ""), level=1)
            doc.add_paragraph(section.get("content", ""))
            
            if "image_path" in section and os.path.exists(section["image_path"]):
                doc.add_picture(section["image_path"], width=DocxInches(5))
                
        filepath = os.path.join(OUTPUT_DIR, filename)
        doc.save(filepath)
        return f"Successfully created DOCX at: {filepath}"
    except Exception as e:
        return f"Error creating DOCX: {str(e)}"

@tool
def create_xlsx(filename: str, sheet_name: str, data: str) -> str:
    """
    Generates an XLSX spreadsheet.
    data must be a JSON string representing a list of dictionaries.
    """
    try:
        import pandas as pd
        data_list = json.loads(data)
        df = pd.DataFrame(data_list)
        
        filepath = os.path.join(OUTPUT_DIR, filename)
        df.to_excel(filepath, index=False, sheet_name=sheet_name)
        return f"Successfully created XLSX at: {filepath}"
    except Exception as e:
        return f"Error creating XLSX: {str(e)}"
    


class DocumentToolset:
    def get_tools(self) -> list:
        return [generate_chart, create_pptx, create_docx, create_xlsx]