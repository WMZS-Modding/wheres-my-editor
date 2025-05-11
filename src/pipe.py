import os
import logging
import numpy as np
from typing import List, Tuple, Optional, Dict
from xml.etree.ElementTree import Element
from lxml import etree

# Define target pipe types
TARGET_PIPES = [
    '/Water/Objects/pipe_new.hs',
    '/Water/Objects/pipe_new_swampy.hs',
    '/Water/Objects/pipe_new_allie.hs',
    '/Water/Objects/pipe_new_cranky.hs'
]

class PathPoints:
    """Class to handle PathPoints data similar to wmwpy's Object class handling of PathPos.
    
    Attributes:
        points (List[Tuple[float, float]]): List of path points
        is_global (bool): Whether points are in global coordinates
        is_closed (bool): Whether the path is closed
        filename (str): The object's filename
    """
    def __init__(self, xml_data: Optional[Element] = None):
        """Initialize PathPoints from XML data.
        
        Args:
            xml_data: XML element containing PathPoints data
        """
        self.points: List[Tuple[float, float]] = []
        self.is_global: bool = False
        self.is_closed: bool = False
        self.filename: str = ""
        
        if xml_data is not None:
            self.readXML(xml_data)
    
    def readXML(self, xml_data: Element) -> None:
        """Read PathPoints data from XML.
        
        Args:
            xml_data: XML element containing PathPoints data
        """
        try:
            # Get object filename
            filename_prop = xml_data.find("./Property[@name='Filename']")
            if filename_prop is not None:
                self.filename = filename_prop.get("value", "")
            
            # Get PathPoints property
            path_points = self._get_property_value(xml_data, "PathPoints")
            if path_points:
                self.points = self._parse_pathpoints(path_points)
            
            # Get global/local setting
            self.is_global = self._get_property_value(xml_data, "PathIsGlobal", "false").lower() == "true"
            
            # Get closed/open setting
            self.is_closed = self._get_property_value(xml_data, "PathIsClosed", "false").lower() == "true"
            
        except Exception as e:
            logging.error(f"Error reading PathPoints XML: {e}")
            self.points = []
    
    def _parse_pathpoints(self, path_points: str) -> List[Tuple[float, float]]:
        """Parse PathPoints string into list of coordinates.
        
        Args:
            path_points: String containing path points data
            
        Returns:
            List of (x,y) coordinate tuples
        """
        try:
            # Remove parentheses and split into points
            points_str = path_points.strip("()").split("),(")
            points = []
            
            for point_str in points_str:
                # Clean up point string and split into x,y
                point_str = point_str.strip("()")
                x, y = map(float, point_str.split(","))
                points.append((x, y))
            
            return points
        except Exception as e:
            logging.error(f"Error parsing PathPoints: {e}")
            return []
    
    def getXML(self) -> etree.ElementBase:
        """Get XML representation of PathPoints.
        
        Returns:
            XML element containing PathPoints data
        """
        xml = etree.Element("Properties")
        
        # Add Filename property
        if self.filename:
            etree.SubElement(xml, "Property", name="Filename", value=self.filename)
        
        # Add PathPoints property
        if self.points:
            points_str = ",".join(f"({x},{y})" for x, y in self.points)
            etree.SubElement(xml, "Property", name="PathPoints", value=points_str)
        
        # Add global/local setting
        etree.SubElement(xml, "Property", name="PathIsGlobal", value=str(self.is_global).lower())
        
        # Add closed/open setting
        etree.SubElement(xml, "Property", name="PathIsClosed", value=str(self.is_closed).lower())
        
        return xml
    
    def transform_points(self, base_pos: Tuple[float, float], scale: float = 1.0) -> List[Tuple[float, float]]:
        """Transform points based on base position and scale.
        
        Args:
            base_pos: Base position (x,y) tuple
            scale: Scale factor
            
        Returns:
            List of transformed (x,y) coordinate tuples
        """
        if not self.points:
            return []
        
        transformed = []
        for x, y in self.points:
            if self.is_global:
                # Global coordinates are already in world space
                transformed.append((x * scale, y * scale))
            else:
                # Local coordinates need to be transformed relative to base position
                transformed.append((
                    (base_pos[0] + x) * scale,
                    (base_pos[1] + y) * scale
                ))
        
        return transformed
    
    def _get_property_value(self, obj: Element, name: str, default: str = "") -> str:
        """Safely extract a property value from an XML object.
        
        Args:
            obj: The XML element to search in
            name: The name of the property to find
            default: Default value to return if property not found
            
        Returns:
            The property value or default if not found
        """
        try:
            prop = obj.find(f"./Property[@name='{name}']")
            return prop.get("value") if prop is not None else default
        except Exception as e:
            logging.error(f"Error getting property {name}: {e}")
            return default

def extract_all_pathpoints(xml_data: Element) -> str:
    """Extract PathPoints data from all pipe objects in XML.
    
    Args:
        xml_data: The XML root element containing level data
        
    Returns:
        Formatted string containing all pipe data
    """
    try:
        output_lines = []
        
        for obj in xml_data.findall(".//Object"):
            filename = _get_property_value(obj, "Filename")
            shortname = os.path.basename(filename) if filename else ""
            
            if not shortname or shortname not in TARGET_PIPES:
                continue
            
            path_points = PathPoints(obj)
            
            output_lines.append(f"Object: {shortname}")
            output_lines.append(f"AbsoluteLocation: {_get_property_value(obj, 'AbsoluteLocation', default='(none)')}")
            output_lines.append(f"Angle: {_get_property_value(obj, 'Angle', default='0.0')}")
            output_lines.append(f"PathPoints: {','.join(f'({x},{y})' for x, y in path_points.points)}")
            output_lines.append(f"PathIsGlobal: {path_points.is_global}")
            output_lines.append(f"PathIsClosed: {path_points.is_closed}")
            output_lines.append("")
        
        return "\n".join(output_lines)
    except Exception as e:
        logging.error(f"Error extracting pathpoints: {e}")
        return "Error extracting pathpoints data"

def _get_property_value(obj: Element, name: str, default: str = "") -> str:
    """Safely extract a property value from an XML object.
    
    Args:
        obj: The XML element to search in
        name: The name of the property to find
        default: Default value to return if property not found
        
    Returns:
        The property value or default if not found
    """
    try:
        prop = obj.find(f"./Property[@name='{name}']")
        return prop.get("value") if prop is not None else default
    except Exception as e:
        logging.error(f"Error getting property {name}: {e}")
        return default
