from collections import defaultdict
from PIL import Image
import numpy as np
# Based on code from Joel Grus
# https://github.com/joelgrus/shirts

def color_dist(image_file):
    """given an image file, return its vector of colors
    (using the quantized colors defined previously)"""
    img = Image.open(image_file)
    num_pixels = img.size[0] * img.size[1]
    # Get color bins (27 bins by default)
    colors, quanta = get_colors()
    #
    color_counts = defaultdict(int)
    for (c,rgb) in img.getcolors(num_pixels):
        color_counts[quantize(rgb, quanta)] += c
    # Return the fraction of total pixels that are that color
    result = [1.0 * color_counts[c] / num_pixels for c in colors]
    return np.array(result)

def quantize(rgb, quanta):
    """map a tuple (r,g,b) each between 0 and 255
    to our discrete color buckets"""
    r,g,b = rgb
    r = max([q for q in quanta if q <= r])
    g = max([q for q in quanta if q <= g])
    b = max([q for q in quanta if q <= b])
    return (r,g,b)

def get_colors():
    NUM_BUCKETS = 3 # this means there will be 3 * 3 * 3 = 27 possible colors

    bucket_size = 256 / NUM_BUCKETS
    quanta = [bucket_size * i for i in range(NUM_BUCKETS)]
    colors = [(r,g,b)
               for r in quanta
               for g in quanta
               for b in quanta]
    return colors, quanta
