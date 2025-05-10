import os

TARGET_PIPES = {
    "pipe_new.hs",
    "pipe_new_swampy.hs",
    "pipe_new_allie.hs",
    "pipe_new_cranky.hs"
}

PIPE_DATA = {}

def load_pipe_data_from_xml(xml_data):
    """Called when loading XML to collect AbsoluteLocation, Angle, PathPoints data"""
    global PIPE_DATA
    PIPE_DATA.clear()

    for obj in xml_data.findall(".//Object"):
        filename = _get_property_value(obj, "Filename")
        shortname = os.path.basename(filename) if filename else ""

        if not shortname or shortname not in TARGET_PIPES:
            continue

        PIPE_DATA[shortname] = {
            "AbsoluteLocation": _get_property_value(obj, "AbsoluteLocation", default="(none)"),
            "Angle": _get_property_value(obj, "Angle", default="0.0"),
            "PathPoints": _get_property_value(obj, "PathPoints", default="(not generated)")
        }

def extract_all_pathpoints(xml_data):
    """Called when clicking the 'Save PathPoints' button to export current data"""
    output_lines = []

    for obj in xml_data.findall(".//Object"):
        filename = _get_property_value(obj, "Filename")
        shortname = os.path.basename(filename) if filename else ""

        if not shortname or shortname not in PIPE_DATA:
            continue

        data = PIPE_DATA[shortname]

        output_lines.append(f"Object: {shortname}")
        output_lines.append(f"AbsoluteLocation: {data.get('AbsoluteLocation')}")
        output_lines.append(f"Angle: {data.get('Angle')}")
        output_lines.append(f"PathPoints: {data.get('PathPoints')}")
        output_lines.append("")

    return "\n".join(output_lines)

def _get_property_value(obj, name, default=""):
    prop = obj.find(f"./Property[@name='{name}']")
    return prop.get("value") if prop is not None else default
