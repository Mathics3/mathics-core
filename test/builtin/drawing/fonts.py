"""
Injects font styling in svg for repeatable text
Courtesy ChatGPT
"""

import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

css = f"""
text, tspan, * {{
    font-family: "Noto Sans" !important;
    font-size: 10px !important;
    font-style: normal !important;
    font-weight: regular !important;
}}
""".strip()


def inject_font_style(svg_text: str) -> str:
    root = ET.fromstring(svg_text)

    style = ET.Element(f"{{{SVG_NS}}}style")
    style.text = css

    root.insert(0, style)
    return ET.tostring(root, encoding="unicode")
