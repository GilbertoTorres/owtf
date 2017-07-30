#!/usr/bin/env python

"""
Pandoc filter to process code blocks with class "plantuml" into
plant-generated images.

Needs `plantuml.jar` from http://plantuml.com/.
"""

import os
import sys
from subprocess import call

from pandocfilters import toJSONFilter, Para, Image, get_caption, get_extension
from helpers import get_filename4code



def plantuml(key, value, format, _):
    if key == 'CodeBlock':
        [[ident, classes, keyvals], code] = value

        if "plantuml" in classes:
            caption, typef, keyvals = get_caption(keyvals)

            tmp_dir = os.path.join(os.getcwd(), '..', '..', '..', 'tmp')
            filename = get_filename4code("plantuml", code, None, tmp_dir)
            filetype = get_extension(format, "png", html="svg", latex="png")

            src = os.path.join(tmp_dir, filename + '.uml')
            dest = os.path.join(tmp_dir, filename + '.' + filetype)

            if not os.path.isfile(dest):
                txt = code.encode(sys.getfilesystemencoding())
                if not txt.startswith("@start"):
                    txt = "@startuml\n" + txt + "\n@enduml\n"
                with open(src, "w") as f:
                    f.write(txt)


                sys.stderr.write('Current dir ' + os.getcwd() + '\n')
                call(["java", "-jar", '../../../../pentype_dependencies/plantuml.jar', "-t"+filetype, src])
                sys.stderr.write('Created image ' + dest + '\n')

            return Para([Image([ident, [], keyvals], caption, [dest, typef])])

if __name__ == "__main__":
    toJSONFilter(plantuml)
