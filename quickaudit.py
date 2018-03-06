#!/usr/bin/env python3
from __future__ import division, print_function
import zbarlight as zbar
from PIL import Image
import sys
from multiprocessing import Pool
from os.path import getsize, splitext
import os
import numpy as np
import rawpy


def qrdecode(image):
    code = zbar.scan_codes('qrcode', image)
    if code is None:
        return []
    return [x.decode('utf8') for x in code]


def load_image(imgpath):
    if imgpath.lower().endswith("cr2"):
        raw = rawpy.imread(imgpath).postprocess()
        raw8 = (raw / 2**16 * 2**8).astype('u1')
        return Image.fromarray(raw8)
    return Image.open(imgpath)


def meanpixel(img):
    return np.array(img).mean()


def audit(imgpath):
    fsize = getsize(imgpath)
    statusstr = "OK"
    qrstr = None
    meanpxstr = None
    try:
        img = load_image(imgpath)
    except:
        statusstr = "IMAGE_LOAD_ERROR"
        qrstr = meanpxstr = 'NA'
    if qrstr is None:
        try:
            qr = qrdecode(img)
            qrstr = ';'.join(sorted(qr)) if qr else 'NOT_DETECTED'
        except:
            qrstr = "QR_ERROR"
    if meanpxstr is None:
        meanpxstr = "{:0.2f}".format(meanpixel(img))
    return (imgpath, fsize, statusstr, qrstr, meanpxstr)

if __name__ == "__main__":
    nthreads = int(os.environ.get("PBS_NCPUS", 1))
    pool = Pool(nthreads)
    print('file\tfile_size_bytes\tstatus\tqrcodes\tmean_pixel_value')

    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        print("Accepting input files from stdin, kill me if you don't want that", file=sys.stderr)
        files = map(lambda f: f.rstrip("\n"), sys.stdin)

    for res in pool.imap_unordered(audit, files):
        print(*res, sep="\t")
