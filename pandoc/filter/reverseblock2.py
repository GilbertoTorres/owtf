#!/usr/bin/env python

"""
Pandoc filter to convert all level 2+ headers to paragraphs with
emphasized text.
"""

import sys

from pandocfilters import toJSONFilter, CodeBlock

def abc(key, value, format, _):
    if key == 'CodeBlock':
        sys.stderr.write('Created image ' + key + '\n')
        [[ident, classes, keyvals], code] = value
        xlist = list(code)
        xlist.reverse()
        rev_code = ''.join(xlist)
        if "rev2" in classes:
            return CodeBlock([ident, ["rev"], keyvals], ">>>" + code + "<<<")

if __name__ == "__main__":
    toJSONFilter(abc)