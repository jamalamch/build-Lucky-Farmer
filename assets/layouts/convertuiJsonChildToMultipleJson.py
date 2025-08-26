#!/usr/bin/env python3
"""
Script to convert ui.json to multiple JSON files.
Each file will contain only one child and be named after that child.
"""

import json
import os
import sys
from pathlib import Path

def extract_name_from_object(obj):
    """Extract the name from a UI object, checking params and other possible locations."""
    if isinstance(obj, dict):
        # Check params.name first
        if 'params' in obj and isinstance(obj['params'], dict) and 'name' in obj['params']:
            return obj['params']['name']
        
        # Check direct name property
        if 'name' in obj:
            return obj['name']
        
        # Check if it has children with names
        if 'children' in obj and isinstance(obj['children'], list):
            for child in obj['children']:
                name = extract_name_from_object(child)
                if name:
                    return name
    
    return None

def find_named_children(children):
    """Find all children that have names or can be identified."""
    named_children = []
    
    for i, child in enumerate(children):
        name = extract_name_from_object(child)
        if name:
            named_children.append((name, child))
        else:
            # If no name found, use index-based naming
            named_children.append((f"child_{i}", child))
    
    return named_children

def convert_ui_json_to_multiple_files(input_file, output_dir):
    """Convert ui.json to multiple JSON files."""
    
    # Read the input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{input_file}': {e}")
        return False
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Extract children from the layout
    if 'layout' not in data or 'children' not in data['layout']:
        print("Error: Expected 'layout.children' structure in JSON file.")
        return False
    
    children = data['layout']['children']
    named_children = find_named_children(children)
    
    print(f"Found {len(named_children)} children to convert:")
    
    # Create separate JSON files for each child
    for name, child in named_children:
        # Sanitize filename
        safe_name = "".join(c for c in name if c.isalnum() or c in ('-', '_')).rstrip()
        if not safe_name:
            safe_name = "unnamed"
        
        filename = f"{safe_name}.json"
        filepath = output_path / filename
        
        # Create the structure for this child
        child_data = {
            "layout": {
                "children": [child]
            }
        }
        
        # Write the file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(child_data, f, indent=2, ensure_ascii=False)
            print(f"  ✓ Created: {filename}")
        except Exception as e:
            print(f"  ✗ Failed to create {filename}: {e}")
    
    print(f"\nConversion completed! Files saved to: {output_dir}")
    return True

def main():
    # Default paths
    script_dir = Path(__file__).parent
    input_file = script_dir / "ui.json"
    output_dir = script_dir / "split_ui"
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_dir = Path(sys.argv[2])
    
    print(f"Converting: {input_file}")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    success = convert_ui_json_to_multiple_files(input_file, output_dir)
    
    if success:
        print("\n🎉 Conversion successful!")
    else:
        print("\n❌ Conversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
