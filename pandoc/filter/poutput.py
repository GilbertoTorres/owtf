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

            poutput_names_resp = requests.get('http://127.0.0.1:8009/api/targets/1/poutput/names/')
            poutput_names_content = poutput_names_resp.content.strip('\n')  # Weird newline chars causing issues
            poutput_names_obj = json.loads(poutput_names_content)

            poutput_plugin_details = []
            for k,v in poutput_names_obj.iteritems():
                for item in v['data']:
                    response = requests.get('http://127.0.0.1:8009/api/targets/1/poutput/?plugin_code=%s' % (k,))
                    content = response.content.strip('\n') # Weird newline chars causing issues
                    poutput_plugin_details.append(json.loads(content))


            if _type == u"index":
                tbl_header = """
---
caption: 'Vulnerabilities Summary'
alignment: C
table-width: 2/3
markdown: True
header: False
---
"""
                tbl_summary = ""
                for k,v in poutput_names_obj.iteritems():
                    details =  v.get('details')
                    tbl_summary += "%s,%s\n" % (details.get('code', ""),details.get('descrip', ""))

                return [CodeBlock([ident, ['table'], keyvals], tbl_header + tbl_summary)]

            elif _type == u"all_detail":
                sys.stderr.write('cvss using type\'' + _type + '\'\n')
                tbl_header = """
---
caption: 'Vulnerabilidies Details'
alignment: C
table-width: 2/3
markdown: True
header: True
---
"""
                result = []
                for k,v in poutput_names_obj.iteritems():
                    details =  v.get('details', {})
                    result.append(Header(2, [slugify(details.get('code', "")), [], []], [Str(details.get('code', "") + " " + details.get('descri', ""))] ))
                    for item in v.get('data'):
                        result.append(Para([Strong([Str("Plugin Type: " + item.get('plugin_type', ""))])]))
                        tbl_detail = ""
                        tbl_detail += "%s,%s,%s\n" % ('RUNTIME', 'TIME INTERVAL', 'STATUS')
                        tbl_detail += "%s,%s,%s\n" % (item.get('run_time',"").replace(',', ''),item.get('start_time',"").replace(',', '') + " - " + item.get('end_time',"").replace(',', ''),item.get('status',""))
                        sys.stderr.write('table detail\'' + tbl_detail + '\'\n')
                        result.append(CodeBlock([ident, ['table'], keyvals], tbl_header + tbl_detail))

                return result
            else:
                raise NotImplementedError()
            
if __name__ == "__main__":
    toJSONFilter(poutput)
