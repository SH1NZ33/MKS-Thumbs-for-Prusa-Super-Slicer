# MKS-Thumbs-for-Prusa-Super-Slicer
Optimized for Wanaho D12 printer

Convert PNG thumbnails from Gcode to MKS thumbnails

Configuration required in the slicer:

- Print Settings > Output Options > Post-processing script : "PythonPath\python.exe" "PythonScript\convert_png-thumbs_to_mks-thumbs.py"
  - Printer Settings > Thumbnails >
    - Size for Gcode
      - Small: x: 100 y: 100
      - Big: x: 200 y: 200
    - Thumbnail option
      - Format of G-code thumbnails: PNG
      - Bed on thumbnail: None
