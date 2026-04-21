#!/usr/bin/env python

import argparse
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

def parse_qgis_bookmarks(file_path):
    """Parses XML and returns a dict keyed by (xmin, ymin, xmax, ymax)."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    bookmarks = list()
    
    for bookmark in root.findall('bookmark'):
        # Extract coordinates and convert to float for consistency
        # Rounding to 6 decimal places (roughly 10cm precision
        
        if bookmark.find('project') is not None:
            prj_name = bookmark.find('project').text
        else:
            prj_name = ""
                    
        # Store data using the coordinate tuple as the unique key
        bookmark_obj = {
            'id': bookmark.find('id').text,
            'name': bookmark.find('name').text,
            'project': prj_name,
            'xmin': bookmark.find('xmin').text,
            'ymin': bookmark.find('ymin').text,
            'xmax': bookmark.find('xmax').text,
            'ymax': bookmark.find('ymax').text,
            'sr_id': bookmark.find('sr_id').text
        }
        if bookmark_obj["project"] == None:
            bookmark_obj["project"] = ""
        
        bookmarks.append(bookmark_obj)
        
    return bookmarks



from collections import defaultdict

def get_bookmark_summary(bookmark_lst):
    """
    Iterates through a list of bookmark dictionaries and returns a 
    hierarchical summary based on Name: Type: Location - Description.
    """
    # Structure: summary[Name][Type] = Count
    summary = defaultdict(lambda: defaultdict(int))
    
    for bm in bookmark_lst:
        full_name = bm.get('name', '')
        
        # Split by ':' to extract Name and Type
        parts = [p.strip() for p in full_name.split(':')]
        
        if len(parts) >= 2:
            name_val = parts[0]
            type_val = parts[1]
            summary[name_val][type_val] += 1
        else:
            summary["Unstructured"]["Other"] += 1
            
    return summary
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs=1, help="Provide the an input XML file for bookmark summary")

    args = parser.parse_args()
    
    bookmarks_file = args.file[0]
    
    if not os.path.exists(bookmarks_file):
        parser.error(f"The file '{bookmarks_file}' does not exist.")
        
    bookmark_lst = parse_qgis_bookmarks(bookmarks_file)
    
    print(f"There are {len(bookmark_lst)} in the input file: {bookmarks_file}")
    
    bookmarks_sum = get_bookmark_summary(bookmark_lst)
    
    print(f"{'Name':<15} | {'Type':<15} | {'Count'}")
    print("-" * 45)
    
    for name, types in sorted(bookmarks_sum.items()):
        total = sum(types.values())
        print(f"{name} (Total: {total})")
        for type_name, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
            print(f"  └── {type_name:<12} : {count}")