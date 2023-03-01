# MKS-Thumbs-for-Prusa-Super-Slicer
Optimized for Wanaho D12 printer

Convert PNG thumbnails from Gcode to MKS thumbnails

Configuration required in the slicer:

- Print Settings > Output Options > Post-processing script : "PythonPath\python.exe" "PythonScript\png2mks_thumbs.py"

![scr01](scr01.png)

- Printer Settings > Thumbnails >
  - Size for Gcode
    - Small: x: 100 y: 100
    - Big: x: 200 y: 200
  - Thumbnail option
    - Format of G-code thumbnails: PNG
    - Bed on thumbnail: None

![scr02](scr02.png)
