#!/usr/bin/env python

"""
Uses Google Chart API
"""

import os
import sys
from subprocess import call
import json

from pandocfilters import toJSONFilter, Para, Image, get_caption, get_extension, get_value
from helpers import get_filename4code



def gchart(key, value, format, _):
    if key == 'CodeBlock':
        [[ident, classes, keyvals], code] = value

        if "gchart" in classes:
            caption, typef, keyvals = get_caption(keyvals)

            tmp_dir = os.path.join(os.getcwd(), '..', '..', '..', 'tmp')
            sys.stderr.write('Created tmp_dir ' + tmp_dir + '\n')
            sys.stderr.write('gchart keyvals\'' + json.dumps(keyvals) + '\'\n')


            filename = get_filename4code("gchart", code, None, tmp_dir)
            # filetype = get_extension(format, "png", html="svg", latex="png")
            filetype = get_extension(format, "png", html="png", latex="png")

            src = os.path.join(tmp_dir, filename + '.json')
            dest = os.path.join(tmp_dir, filename + '.' + filetype)

            _type, keyvals = get_value(keyvals, u"type", u"LineChart")
            sys.stderr.write('gchart type\'' + json.dumps(_type) + '\'\n')

            if not os.path.isfile(dest):
                txt = code.encode(sys.getfilesystemencoding())
                with open(src, "w") as f:
                    f.write(txt)

                phantomjs_bin = "phantomjs"
                gchart_script = "../scripts/gchart.js"
                call([phantomjs_bin, gchart_script, _type, dest, txt])
                sys.stderr.write('Created image ' + dest + '\n')

            return Para([Image([ident, [], keyvals], caption, [dest, typef])])

if __name__ == "__main__":
    toJSONFilter(gchart)
