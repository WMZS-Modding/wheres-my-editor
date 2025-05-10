TARGET_PIPES = {
    "pipe_new.hs",
    "pipe_new_swampy.hs",
    "pipe_new_allie.hs",
    "pipe_new_cranky.hs"
}

PIPE_DATA = {}  # key = filename, value = dict

def load_pipe_data_from_xml(xml_data):
    """Call in loadLevel to load initial data"""
    global PIPE_DATA
    PIPE_DATA.clear()

    for obj in xml_data.findall(".//Object"):
        filename = _get_property_value(obj, "Filename")
        if not filename or not any(pipe in filename for pipe in TARGET_PIPES):
            continue

        PIPE_DATA[filename] = {
            "AbsoluteLocation": _get_property_value(obj, "AbsoluteLocation", default="(none)"),
            "Angle": _get_property_value(obj, "Angle", default="0.0"),
            "PathPoints": "(not generated)"
        }

def extract_all_pathpoints(xml_data):
    """Called when the user presses Save PathPoints"""
    output_lines = []

    for obj in xml_data.findall(".//Object"):
        filename = _get_property_value(obj, "Filename")
        if not filename or filename not in PIPE_DATA:
            continue

        data = PIPE_DATA[filename]

        output_lines.append(f"Object: {filename}")
        output_lines.append(f"AbsoluteLocation: {data.get('AbsoluteLocation')}")
        output_lines.append(f"Angle: {data.get('Angle')}")
        output_lines.append(f"PathPoints: {data.get('PathPoints')}")
        output_lines.append("")

    return "\n".join(output_lines)

def _get_property_value(obj, name, default=""):
    prop = obj.find(f"./Property[@name='{name}']")
    return prop.get("value") if prop is not None else default
