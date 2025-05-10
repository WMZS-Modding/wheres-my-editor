import os

TARGET_PIPES = {
    "pipe_new.hs",
    "pipe_new_swampy.hs",
    "pipe_new_allie.hs",
    "pipe_new_cranky.hs"
}

def extract_all_pathpoints(xml_data):
    output_lines = []

    for obj in xml_data.findall(".//Object"):
        filename_prop = obj.find("./Property[@name='Filename']")
        if filename_prop is None:
            continue

        filename = filename_prop.get("value", "")
        if not any(pipe in filename for pipe in TARGET_PIPES):
            continue

        abs_loc = _get_property_value(obj, "AbsoluteLocation", default="(none)")
        angle = _get_property_value(obj, "Angle", default="0.0")

        output_lines.append(f"Object: {filename}")
        output_lines.append(f"AbsoluteLocation: {abs_loc}")
        output_lines.append(f"Angle: {angle}")
        output_lines.append("PathPoints: (not generated)")
        output_lines.append("")

    return "\n".join(output_lines)

def _get_property_value(obj, name, default=""):
    prop = obj.find(f"./Property[@name='{name}']")
    return prop.get("value") if prop is not None else default
