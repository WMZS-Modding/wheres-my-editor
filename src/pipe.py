import os
import subprocess
import tempfile

TARGET_PIPES = {
    "pipe_new.hs",
    "pipe_new_swampy.hs",
    "pipe_new_allie.hs",
    "pipe_new_cranky.hs"
}

def extract_all_pathpoints(xml_data, image_folder=None):
    output_lines = []

    for obj in xml_data.findall(".//Object"):
        filename_prop = obj.find("./Property[@name='Filename']")
        if filename_prop is None:
            continue

        filename = filename_prop.get("value", "")
        if not any(pipe in filename for pipe in TARGET_PIPES):
            continue

        img_path = _find_image_path(filename, image_folder)
        if not img_path or not os.path.exists(img_path):
            output_lines.append(f"# Missing image for {filename}")
            continue

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_out:
            temp_output_path = temp_out.name

        try:
            subprocess.run(["python", "PathPointsExtractor.py", img_path, "-o", temp_output_path], check=True)
            with open(temp_output_path, "r") as f:
                pathpoints = f.read().strip()
        except Exception as e:
            pathpoints = f"ERROR: {e}"
        finally:
            if os.path.exists(temp_output_path):
                os.remove(temp_output_path)

        abs_loc = _get_property_value(obj, "AbsoluteLocation", default="(none)")
        angle = _get_property_value(obj, "Angle", default="0.0")

        output_lines.append(f"Object: {filename}")
        output_lines.append(f"AbsoluteLocation: {abs_loc}")
        output_lines.append(f"Angle: {angle}")
        output_lines.append(f"PathPoints: {pathpoints}")
        output_lines.append("")

    return "\n".join(output_lines)

def _get_property_value(obj, name, default=""):
    prop = obj.find(f"./Property[@name='{name}']")
    return prop.get("value") if prop is not None else default

def _find_image_path(filename, image_folder):
    if not image_folder:
        return None

    base = os.path.splitext(os.path.basename(filename))[0]
    candidates = [base + ext for ext in [".png", ".webp", ".waltex"]]

    for fname in candidates:
        full_path = os.path.join(image_folder, fname)
        if os.path.exists(full_path):
            if fname.endswith(".waltex"):
                return _convert_waltex(full_path)
            return full_path
    return None

def _convert_waltex(waltex_path):
    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    try:
        subprocess.run(["python", "waltex.py", waltex_path, output_path], check=True)
    except Exception:
        return None
    return output_path if os.path.exists(output_path) else None
