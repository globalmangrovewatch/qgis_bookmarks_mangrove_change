# QGIS Bookmarks for Mangrove Change

Repo for sharing QGIS bookmarks of where there are interesting areas (e.g., changes) in mangroves.

## QGIS Bookmarks Structure

The QGIS spatial bookmarks are stored as an XML file - note each time you export, the IDs get replaced...

```
<bookmark>
  <id>{bf05e1ae-76b2-4c20-9468-63ebcb3b57db}</id>
  <name>GMW: Dynamic: Australia, QLD - Dynamic coastal spur</name>
  <project/>
  <xmin>140.90373803700001076</xmin>
  <ymin>-17.11519509200000044</ymin>
  <xmax>140.99232985099999382</xmax>
  <ymax>-17.01990738599999986</ymax>
  <rotation>0</rotation>
  <sr_id>3452</sr_id>
</bookmark>
```

I've proposed the following naming convention:

```
<Name>: <type>: <Country/Location> - <Description>
```

For example:
```
GMW: Dynamic: Australia, QLD - Dynamic coastal spur
```


| Types  | Description |
| ------------- | ------------- |
| Dynamic  | Examples where there is both gain and loss.  |
| Gain  | Examples where it is mainly gain or at least that is the interesting element.  |
| Loss  | Examples where it is mainly loss or at least that is the interesting element.  |

## Python Tools

The Python tool `tools/qgis_merge_bookmarks.py` has been provided to help support merging spatial bookmarks, as you cannot just export selected bookmarks from QGIS. 

Note, the two input XMLs are ordered. The first XML file you provide will be the base file, and its information will be used for bookmarks common to both files. This means that if you change the name of the bookmark in the second file, this will be ignored and not copied over to the output. Only bookmarks which are not present in first file will be copied across.



## Workflow

1) Export your bookmarks from QGIS

2) Use `qgis_merge_bookmarks.py` to compute the difference between those in the repo and the ones you have exported - output to XML.

   ```
   python qgis_merge_bookmarks.py --clearproj -d -o diffs.xml ../gmw_qgis_bookmarks.xml exported_qgis_bookmarks.xml
   ```

3) Check the `diffs.xml` and remove any bookmarks you do not want to merge

4) Use `qgis_merge_bookmarks.py` to merge the bookmarks in the repo and your `diffs.xml`

   ```
   python qgis_merge_bookmarks.py -o gmw_qgis_bookmarks.xml ../gmw_qgis_bookmarks.xml diffs.xml

   ```

5) Output summary of bookmarks (`qgis_bookmark_summary.py`) to check that output file is valid and has the entries you expect
  ```
   python qgis_bookmark_summary.py gmw_qgis_bookmarks.xml

   ```

7) Move the `gmw_qgis_bookmarks.xml` file to replace the existing file in the repo.
  
8) Commit changes to the repo.




### Simple Usage:

Will just report the number in common and the differences between the two files

```
python tools/qgis_merge_bookmarks.py gmw_qgis_bookmarks.xml exported_qgis_bookmarks.xml
```

### Difference Usage:

Will report the number in common and the differences between the two files, but will also print the differences to the console:

```
python tools/qgis_merge_bookmarks.py -d gmw_qgis_bookmarks.xml exported_qgis_bookmarks.xml
```

Will report the number in common and the differences between the two files, but will export the differences to a new XML file:

```
python tools/qgis_merge_bookmarks.py -d -o diffs.xml gmw_qgis_bookmarks.xml exported_qgis_bookmarks.xml
```

### Merge Usage:

Will report the number in common and the differences between the two files, and will export an XML file with the union of the two input XML files.

```
python tools/qgis_merge_bookmarks.py -o merged_bookmarks.xml gmw_qgis_bookmarks.xml exported_qgis_bookmarks.xml
```

If the output file already exists and you want to overwrite it, then you will need to include the `--overwrite` switch

```
python tools/qgis_merge_bookmarks.py -o merged_bookmarks.xml --overwrite gmw_qgis_bookmarks.xml exported_qgis_bookmarks.xml
```

### Remove Project Names Usage:

The `--clearproj` switch will clear project names if they are present in either of the two input XML files.

```
python tools/qgis_merge_bookmarks.py -o merged_bookmarks.xml --overwrite --clearproj gmw_qgis_bookmarks.xml exported_qgis_bookmarks.xml
```


### Summarise bookmarks list
Using the expected structure `<Name>: <type>: <Country/Location> - <Description>` summarise the number of bookmarks for the `name` and `type`.

```
python tools/qgis_bookmark_summary.py gmw_qgis_bookmarks.xml
```


