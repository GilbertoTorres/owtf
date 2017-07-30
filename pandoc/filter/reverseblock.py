#!/usr/bin/env python

"""
Pandoc filter to convert all level 2+ headers to paragraphs with
emphasized text.
"""

import os
import sys
from subprocess import Popen, PIPE, call

from pandocfilters import toJSONFilter, Emph, Para, Str, Image, get_caption, get_filename4code, get_extension
import json

def abc2eps(abc_src, filetype, outfile):
    p = Popen(["abcm2ps", "-O", outfile + '.eps', "-"], stdin=PIPE)
    p.stdin.write(abc_src)
    p.communicate()
    p.stdin.close()
    call(["convert", outfile + '.eps', outfile + '.' + filetype])


def abc(key, value, format, _):
    if key == 'CodeBlock':
        sys.stderr.write('Created image ' + key + '\n')
        [[ident, classes, keyvals], code] = value
        xlist = list(code)
        xlist.reverse()
        rev_code = ''.join(xlist)
        if "rev" in classes:
            sys.stderr.write('Created image ' + json.dumps(value) + '\n')
        #     caption, typef, keyvals = get_caption(keyvals)
        #     outfile = get_filename4code("abc", code)
        #     filetype = get_extension(format, "png", html="png", latex="pdf")
        #     dest = outfile + '.' + filetype

        #     if not os.path.isfile(dest):
        #         abc2eps(code.encode("utf-8"), filetype, outfile)
        #         sys.stderr.write('Created image ' + dest + '\n')

            return Para([Str(rev_code)])


if __name__ == "__main__":
    toJSONFilter(abc)