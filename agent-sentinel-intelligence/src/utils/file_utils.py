"""
File utility functions for Agent Sentinel Intelligence Layer.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


def read_security_report(file_path: Optional[str] = None) -> str:
    """
    Read a security report from file.
    
    Args:
        file_path: Optional specific file path
        
    Returns:
        Report content as string
        
    Raises:
        FileNotFoundError: If no report file is found
    """
    if file_path:
        path = Path(file_path)
        if path.exists():
            try:
                with open(path, "r") as f:
                    content = f.read()
                logger.info("Read security report from: %s", file_path)
                return content
            except Exception as e:
                logger.error("Failed to read %s: %s", file_path, e)
                raise
    
    # Look for common security report files
    possible_files = [
        "real_a2a_security_report_20250713_012303.txt",
        "security_report.txt",
        "agent_sentinel_report.json",
        "unified_report.json",
        "sentinel_report.json"
    ]
    
    for filename in possible_files:
        path = Path(filename)
        if path.exists():
            try:
                with open(path, "r") as f:
                    content = f.read()
                logger.info("Read security report from: %s", filename)
                return content
            except Exception as e:
                logger.warning(f"⚠️  Failed to read {filename}: {e}")
    
    raise FileNotFoundError(
        "No security report file found. Please ensure a security report file is available "
        "in the current directory with one of these names: "
        + ", ".join(possible_files)
    )


def save_report(
    content: str, 
    filename: str, 
    output_dir: Path = Path("./reports"),
    formats: Optional[List[str]] = None
) -> Dict[str, str]:
    """
    Save a report in multiple formats.
    
    Args:
        content: Report content to save
        filename: Base filename without extension
        output_dir: Output directory
        formats: List of formats to save (default: ["txt", "json"])
        
    Returns:
        Dictionary mapping format to file path
    """
    if formats is None:
        formats = ["txt", "json"]
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = {}
    
    # Save text file
    if "txt" in formats:
        txt_path = output_dir / f"{filename}.txt"
        try:
            with open(txt_path, "w") as f:
                f.write("AGENT SENTINEL SECURITY REPORT\n")
                f.write("=" * 60 + "\n\n")
                f.write(content)
            saved_files["txt"] = str(txt_path)
            logger.info("Text report saved to: %s", txt_path)
        except Exception as e:
            logger.error("Failed to save text report: %s", e)
    
    # Save JSON file
    if "json" in formats:
        json_path = output_dir / f"{filename}.json"
        try:
            report_data = {
                "report_type": "security_analysis",
                "content": content,
                "metadata": {
                    "generated_by": "agent_sentinel_intelligence",
                    "format": "text"
                }
            }
            with open(json_path, "w") as f:
                json.dump(report_data, f, indent=2)
            saved_files["json"] = str(json_path)
            logger.info("JSON report saved to: %s", json_path)
        except Exception as e:
            logger.error("Failed to save JSON report: %s", e)
    
    return saved_files


def read_json_report(file_path: str) -> Dict[str, Any]:
    """
    Read a JSON report file.
    
    Args:
        file_path: Path to JSON report file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Report file not found: {file_path}")
    
    try:
        with open(path, "r") as f:
            data = json.load(f)
        logger.info("Read JSON report from: %s", file_path)
        return data
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in %s: %s", file_path, e)
        raise
    except Exception as e:
        logger.error("Failed to read %s: %s", file_path, e)
        raise 