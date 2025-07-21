# styler.py
import json
from docx import Document
from docx.shared import Pt, RGBColor

def apply_styles_to_docx(docx_path, json_path, output_path):
    doc = Document(docx_path)
    with open(json_path, 'r') as f:
        styles_config = json.load(f)

    for style_name, props in styles_config.items():
        try:
            style = doc.styles[style_name]
            font = style.font
            if 'font' in props:
                font.name = props['font']
            if 'size' in props:
                font.size = Pt(props['size'])
            if 'color' in props:
                font.color.rgb = RGBColor.from_string(props['color'])
            if 'bold' in props:
                font.bold = props['bold']
            if 'italic' in props:
                font.italic = props['italic']
        except KeyError:
            print(f"Warning: Style '{style_name}' not found in document.")

    doc.save(output_path)
    print(f"Styled DOCX saved to {output_path}")
