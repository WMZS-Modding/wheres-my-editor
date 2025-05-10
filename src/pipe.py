import os
import logging
from typing import Set, Optional
from xml.etree.ElementTree import Element

# Define target pipe types
TARGET_PIPES = [
    '/Water/Objects/pipe_new.hs',
    '/Water/Objects/pipe_new_swampy.hs',
    '/Water/Objects/pipe_new_allie.hs',
    '/Water/Objects/pipe_new_cranky.hs'
]

def load_pipe_data_from_xml(xml_data: Element) -> None:
    """
    Called when loading XML to collect AbsoluteLocation, Angle, PathPoints data.
    This function is now a no-op since we read directly from XML when needed.
    
    Args:
        xml_data: The XML root element containing level data
    """
    # This function is kept for backward compatibility
    # but no longer needs to store data
    pass

def extract_all_pathpoints(xml_data: Element) -> str:
    """
    Called when clicking the 'Save PathPoints' button to export current data.
    Reads directly from the XML to ensure latest values are exported.
    
    Args:
        xml_data: The XML root element containing level data
        
    Returns:
        str: Formatted string containing all pipe data
    """
    try:
        output_lines = []

        for obj in xml_data.findall(".//Object"):
            filename = _get_property_value(obj, "Filename")
            shortname = os.path.basename(filename) if filename else ""

            if not shortname or shortname not in TARGET_PIPES:
                continue

            output_lines.append(f"Object: {shortname}")
            output_lines.append(f"AbsoluteLocation: {_get_property_value(obj, 'AbsoluteLocation', default='(none)')}")
            output_lines.append(f"Angle: {_get_property_value(obj, 'Angle', default='0.0')}")
            output_lines.append(f"PathPoints: {_get_property_value(obj, 'PathPoints', default='(not generated)')}")
            output_lines.append("")

        return "\n".join(output_lines)
    except Exception as e:
        logging.error(f"Error extracting pathpoints: {e}")
        return "Error extracting pathpoints data"

def _get_property_value(obj: Element, name: str, default: str = "") -> str:
    """
    Safely extract a property value from an XML object.
    
    Args:
        obj: The XML element to search in
        name: The name of the property to find
        default: Default value to return if property not found
        
    Returns:
        str: The property value or default if not found
    """
    try:
        prop = obj.find(f"./Property[@name='{name}']")
        return prop.get("value") if prop is not None else default
    except Exception as e:
        logging.error(f"Error getting property {name}: {e}")
        return default
