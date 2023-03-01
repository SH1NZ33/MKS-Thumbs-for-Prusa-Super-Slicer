#!/usr/local/bin/python3
"""
    replace prusa/superslicer thumbnails (png) to mks thumbnails
    optimized for wanhao D12

    (c) Shinzee

    Requiered from slicer app (PrusaSlicer / SuperSlicer)
    Print Settings > Output Options > Post-processing script : "PythonPath\python.exe" "PythonScript\convert_png-thumbs_to_mks-thumbs.py"
    Printer Settings > Thumbnails >
        Size for Gcode
            Small: x: 100 y: 100
            Big: x: 200 y: 200
        Thumbnail option
            Format of G-code thumbnails: PNG
            Bed on thumbnail: None
"""
import os, sys, re, base64
from PIL import Image
from io import BytesIO
from os.path import exists, dirname

cur_dir = dirname(__file__)

#--------------------------------------------------------------------------------------------------
def add_leading_zeros(rgb):
    return "{:0>4x}".format(rgb)

#--------------------------------------------------------------------------------------------------
def join_lines(datas, start_row, end_row):
    return ''.join(datas[start_row-1:end_row])

#--------------------------------------------------------------------------------------------------
def convert_color_to_RGB16(color_rgb, swap = True, inverted = False):
    """ 
    Convert RBG to RGB565
    
    5 bits -> RED
    6 bits -> GREEN
    5 bits -> BLUE
    5 + 6 + 5 --> 16 bits

    output : string of 4 chars
    """
    if inverted:
        b = color_rgb[0] >> 3
        g = color_rgb[1] >> 2
        r = color_rgb[2] >> 3
    else:
        r = color_rgb[0] >> 3
        g = color_rgb[1] >> 2
        b = color_rgb[2] >> 3

    rgb = (r << 11) | (g << 5) | b

    if not swap:
        return add_leading_zeros(rgb)
    
    swap_string_low = rgb >> 8
    swap_string_high = (rgb & 0x00FF) << 8
    swap_string = swap_string_low | swap_string_high
    return add_leading_zeros(swap_string)


#--------------------------------------------------------------------------------------------------
def generate_preview(img, img_type = "", swap = True, inverted = False):
    """ 
        convert image (PIL) into MKS thumbnail 
        return a multilines string
    """
    width, height = img.size
    res = ""
    for _i, y in enumerate(range(height)):
        line = img_type if _i == 0 else '\rM10086 ;'
        for x in range(width):
            pixel_rgb = img.getpixel((x, y))
            pixel_hex = convert_color_to_RGB16(pixel_rgb, swap, inverted)
            line += pixel_hex
        res += line
    return res

#--------------------------------------------------------------------------------------------------
def get_thumbs(datas):
    """
    return a dictionnary with all thumbnails found
    input : full gcode (string)
    """
    if type(datas).__name__ == 'list':
        datas = ''.join(datas)
    # regex method to get all datas needed from matches (groups)
    pattern = re.compile(r"; thumbnail begin (\d+)x(\d+) (\d+)\n; (.+?)\n; thumbnail end", re.DOTALL)
    matches = list(pattern.finditer(datas))

    #remove unwanted chars
    table = str.maketrans("", "", "\n ;") 

    #return list of dictionnaries
    return [
        {
            'width': match.group(1),
            'height': match.group(2),
            'size': match.group(3),
            'base64': ''.join(match.groups()[3:]).translate(table),
            'start_row': datas.count("\n", 0, match.start()),
            'end_row': datas.count("\n", 0, match.end())
        }
        for match in matches
    ]

#--------------------------------------------------------------------------------------------------
def get_previews(thumbs):
    """ 
    decode png thumbails into images (PIL)
    return 2 images
    """
    large_preview, small_preview = None, None
    for t in thumbs:
        with BytesIO(base64.b64decode(t["base64"])) as stream:
            image = Image.open(stream).convert("RGB")
        if (image.height == image.width):
            large_preview = image if image.height == 200 else large_preview
            small_preview = image if image.height in [100, 50] else small_preview

    return large_preview, small_preview

#--------------------------------------------------------------------------------------------------
def save(gfile, large_preview, small_preview, thumbs, datas):
    """
    replace png thumbnails to mks thumbnais into gcode file 
    """
    row = 1
    with open(gfile, "w") as f:
        start_row, end_row, height = thumbs[0]["start_row"], thumbs[0]["end_row"], thumbs[0]["end_row"]
        if start_row > row:
            f.write( join_lines(datas, 1, start_row - 1) )
            row += end_row
        f.write( generate_preview(small_preview, ";simage:") )
        f.write('\rM10086 ;\n')
        start_row, end_row, height = thumbs[1]["start_row"], thumbs[1]["end_row"], thumbs[1]["end_row"]
        f.write( generate_preview(large_preview, ";;gimage:", swap = True, inverted = True) )
        f.write('\rM10086 ;\n')
        f.write( join_lines(datas, end_row + 1, len(datas)) )

#--------------------------------------------------------------------------------------------------
def do_convert(gfile):
    """
    open gcode file, convert and ovewrite gcode file
    """
    with open(gfile, "r") as g_gile:
        datas = g_gile.readlines()

    thumbs = get_thumbs(datas)   
    large_preview, small_preview = get_previews(thumbs)
    save(gfile, large_preview, small_preview, thumbs, datas)
    

#--------------------------------------------------------------------------------------------------
def main(argv):
    """
    execute convertion from gcode path (called by slicer / args)
    """
    os.system('cls' if os.name == 'nt' else 'clear') 
    inputfile = ''

    try:
        inputfile = sys.argv[1]
    except Exception:
        print('fail on inputfile')
        sys.exit()

    do_convert(inputfile)
    print("OK")

  
#--------------------------------------------------------------------------------------------------
if __name__ == "__main__":
   main(sys.argv[1:])
