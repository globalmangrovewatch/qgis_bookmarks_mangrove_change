#!/usr/bin/env python

import argparse
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

def parse_qgis_bookmarks(file_path):
    """Parses XML and returns a dict keyed by (xmin, ymin, xmax, ymax)."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    bookmarks = {}
    
    for bookmark in root.findall('bookmark'):
        # Extract coordinates and convert to float for consistency
        # Rounding to 6 decimal places (roughly 10cm precision)
        coords = (
            round(float(bookmark.find('xmin').text), 6),
            round(float(bookmark.find('ymin').text), 6),
            round(float(bookmark.find('xmax').text), 6),
            round(float(bookmark.find('ymax').text), 6)
        )
        
        if bookmark.find('project') is not None:
            prj_name = bookmark.find('project').text
        else:
            prj_name = ""
                    
        # Store data using the coordinate tuple as the unique key
        bookmarks[coords] = {
            'id': bookmark.find('id').text,
            'name': bookmark.find('name').text,
            'project': prj_name,
            'xmin': bookmark.find('xmin').text,
            'ymin': bookmark.find('ymin').text,
            'xmax': bookmark.find('xmax').text,
            'ymax': bookmark.find('ymax').text,
            'sr_id': bookmark.find('sr_id').text
        }
        if bookmarks[coords]["project"] == None:
            bookmarks[coords]["project"] = ""
        
    return bookmarks


def compare_bookmarks(bookmarks_f1, bookmarks_f2):
    bboxes1 = set(bookmarks_f1.keys())
    bboxes2 = set(bookmarks_f2.keys())

    common_coords = bboxes1.intersection(bboxes2)
    common_lst = [bookmarks_f1[c] for c in common_coords]

    # 2. Differences: Exists in one but not the other
    unique_coords = bboxes1.symmetric_difference(bboxes2)
    unique_lst = []
    for c in unique_coords:
        if c in bookmarks_f1:
            unique_lst.append(bookmarks_f1[c])
        else:
            unique_lst.append(bookmarks_f2[c])

    return common_lst, unique_lst
    
    
def export_bookmarks_to_xml(bookmark_lst, output_file):
    """
    Converts a list of bookmark dictionaries into a QGIS-compatible XML file.
    """
    # Sort the list of dictionaries by the 'id' key
    # We use .get('id', '') to handle cases where an name might be missing
    sorted_bookmark_lst = sorted(bookmark_lst, key=lambda x: x.get('name', '').lower())
    
    # Create the root element with the required QGIS tag
    root = ET.Element("qgis_bookmarks")

    for bm in sorted_bookmark_lst:
        bookmark_node = ET.SubElement(root, "bookmark")
        
        # Define the expected tags in order
        tags = ['id', 'name', 'project', 'xmin', 'ymin', 'xmax', 'ymax', 'rotation', 'sr_id']
        
        for tag in tags:
            child = ET.SubElement(bookmark_node, tag)
            # Use .get() to provide a default value if a key is missing
            value = bm.get(tag, "")
            
            # Ensure rotation defaults to 0 if not present
            if tag == 'rotation' and value == "":
                value = "0"
                
            child.text = str(value)

    # Convert to string and use minidom for pretty formatting
    xml_string = ET.tostring(root, encoding='utf-8')
    reparsed = minidom.parseString(xml_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    # Write to file
    with open(output_file, "w", encoding="utf-8") as f:
        # QGIS XML files usually start with the DOCTYPE and the XML declaration
        f.write('<!DOCTYPE qgis_bookmarks>\n')
        f.write(pretty_xml.replace('<?xml version="1.0" ?>\n', ''))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite the output vector file, if not specified "
             "then layer will be added to exisitng file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        help="Output XML file.",
    )
    
    parser.add_argument(
        "-d",
        "--diff",
        action="store_true",
        default=False,
        help="Print/Output the additional bookmarks to the console, if an output file path is provided.",
    )
    
    parser.add_argument(
        "--clearproj",
        action="store_true",
        default=False,
        help="Clears the project name for all the bookmarks.",
    )

        
    parser.add_argument("files", nargs=2, help="Provide the two input XML files for comparison")

    args = parser.parse_args()
    
    
    for file_path in args.files:
        if not os.path.exists(file_path):
            parser.error(f"The file '{file_path}' does not exist.")
    
    create_output = False
    if args.output and os.path.isdir(args.output):
        parser.error(f"The output path '{args.output}' is a directory, not a file.")
    elif args.output and os.path.exists(args.output) and (not args.overwrite):
        parser.error(f"The output path '{args.output}' already exists, you need to use the --overwrite option.")
    elif args.output:
        create_output = True
    
    bookmarks_file1 = args.files[0]
    bookmarks_file2 = args.files[1]
    
    print(bookmarks_file1)
    print(bookmarks_file2)
    
    bookmarks_f1 = parse_qgis_bookmarks(bookmarks_file1)
    bookmarks_f2 = parse_qgis_bookmarks(bookmarks_file2)
    
    common_bookmarks_lst, unq_bookmarks_lst = compare_bookmarks(bookmarks_f1, bookmarks_f2)
    
    if args.clearproj:
        for i, bookmark in enumerate(common_bookmarks_lst):
            common_bookmarks_lst[i]["project"] = ""
        for i, bookmark in enumerate(unq_bookmarks_lst):
            unq_bookmarks_lst[i]["project"] = ""
    
    n_xtra_bookmarks = len(unq_bookmarks_lst)
    n_common_bookmarks = len(common_bookmarks_lst)
    
    print(f"There are {n_common_bookmarks} bookmarks in common between the two files.")
    print(f"There are {n_xtra_bookmarks} bookmarks which are only in one of the two files.")
    
    if args.diff:
        import pprint
        pprint.pprint(unq_bookmarks_lst)
    
    if create_output:
        print("Creating output file")
        if args.diff:
            slg_bookmark_lst = unq_bookmarks_lst
        else:
            slg_bookmark_lst = common_bookmarks_lst + unq_bookmarks_lst
        
        export_bookmarks_to_xml(slg_bookmark_lst, args.output)