#!/usr/bin/env python

"""
Plugin Output Filter
"""


import requests
import json

from pandocfilters import toJSONFilter, CodeBlock, Para, Image, get_caption, get_extension, get_value


def poutput(key, value, format, _):
    if key == 'CodeBlock':
        [[ident, classes, keyvals], code] = value

        if "poutput" in classes:
            response = requests.get('http://192.168.0.10:8009/api/targets/1/poutput/names/')
            content = response.content
            content = content.strip('\n') # Weird newline chars causing issues
            output = json.loads(content)

            tbl = """
---
caption: 'Tests Ejecutados'
alignment: C
table-width: 2/3
markdown: True
---
Tests Ejecutados
"""
            tests = "\n".join(output.keys())

            tbl += tests
            return CodeBlock([ident, ['table'], keyvals], tbl)

if __name__ == "__main__":
    toJSONFilter(poutput)
