#!/usr/bin/env python

"""
Plugin Output Filter
"""

import sys
import requests
import json
from slugify import slugify

from pandocfilters import toJSONFilter, Header, CodeBlock, Space, Para, Str, Strong, Emph, Image, get_caption, get_extension, get_value


def text2pandoc(str):
    result = []
    arr = str.split(" ")
    if len(arr) > 0:
        result.append(Str(arr[0]))
    for x in arr[1:]:
        result.append(Space)
        result.append(Str(x))
    return result


def poutput(key, value, format, _):
    if key == 'CodeBlock':
        [[ident, classes, keyvals], code] = value

        if "poutput" in classes:
            _type, keyvals = get_value(keyvals, u"type", u"index")

            response = requests.get('http://127.0.0.1:8009/api/targets/1/poutput/names/')
            content = response.content
            content = content.strip('\n') # Weird newline chars causing issues
            output = json.loads(content)

            if _type == u"index":
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
                return [CodeBlock([ident, ['table'], keyvals], tbl)]
            elif _type == u"all_detail":
                sys.stderr.write('cvss using type\'' + _type + '\'\n')
                tbl_detail = """
---
caption: 'Tests Ejecutados'
alignment: C
table-width: 2/3
markdown: True
---
Tests Ejecutados
"""
                result = []
                for k,v in output.iteritems():
                    content = k
                    result.append(Header(2, [slugify(content), [], []], text2pandoc(content)))
                    for item in v['data']:
                        tests = ",".join(['RUNTIME', 'TIME INTERVAL', 'STATUS'])
                        tests += "\n"+",".join([item['run_time'].replace(","," "), "%s - %s" % (item['start_time'],item['end_time']), item['status']])
                        result.append(CodeBlock([ident, ['table'], keyvals], tbl_detail + tests))
                        response = requests.get('http://127.0.0.1:8009/api/targets/1/poutput/?plugin_code=%s' % (k,))
                        content = response.content
                        content = content.strip('\n') # Weird newline chars causing issues
                        output = json.loads(content)
                return result
            else:
                raise NotImplementedError()
            
if __name__ == "__main__":
    toJSONFilter(poutput)
