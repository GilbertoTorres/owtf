#!/usr/bin/env python

"""
Uses Google Chart API
"""

import os
import sys
from subprocess import Popen, PIPE
import json

from pandocfilters import toJSONFilter, CodeBlock, Para, Image, get_caption, get_extension, get_value
from helpers import get_filename4code


def cvss(key, value, format, _):
    if key == 'CodeBlock':
        [[ident, classes, keyvals], code] = value

        if "cvss" in classes:
            caption, typef, keyvals = get_caption(keyvals)
            sys.stderr.write('cvss keyvals\'' + json.dumps(keyvals) + '\'\n')
            sys.stderr.write('cvss caption\'' + json.dumps(caption) + '\'\n')
            _version, keyvals = get_value(keyvals, u"version", u"3")

            if _version == u"3":
                sys.stderr.write('cvss using version\'' + _version + '\'\n')
            else:
                raise NotImplementedError()
            node_bin = "node"
            cvss_script = "../scripts/run_cvsscalc30.js"
            p = Popen([node_bin, cvss_script, code.strip()], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate()
            rc = p.returncode
            sys.stderr.write('cvss input\'' + code + '\'\n')
            sys.stderr.write('cvss output\'' + output + '\'\n')

            obj = json.loads(output)
            sys.stderr.write('cvss output\'' + obj['baseMetricScore'] + '\'\n')


            code = """
{
    "data": [
        ["Metric", "Score", { "role": "style" }, { "role": "annotation" } ],
        ["Base", %s, "#7CC000", "%s"],
        ["Impact", %s, "#7CC000", "%s"],
        ["Exploitability", %s, "#7CC000", "%s"],
        ["Temporal", %s, "#55ACD1", "%s"],
        ["Environmental", %s, "#DC9100", "%s"],
        ["Modified Impact", %s, "#FAC13D", "%s"]
      ],
    "options": {"legend": "none" }
}
""" % (obj['baseMetricScore'],obj['baseMetricScore'],
        obj['impactSubScore'],obj['impactSubScore'],
        obj['exploitabalitySubScore'],obj['exploitabalitySubScore'],
        obj['temporalMetricScore'],obj['temporalMetricScore'],
        obj['environmentalMetricScore'],obj['environmentalMetricScore'],
        obj['envModifiedImpactSubScore'],obj['envModifiedImpactSubScore'],
        )
            sys.stderr.write('cvss code\'' + code + '\'\n')
            keyvals.append(["type", "ColumnChart"])
            keyvals.append(["width", "600px"])
            # keyvals.append(["caption", caption[0]['c']])
            return CodeBlock([ident, ["gchart"], keyvals], code)

if __name__ == "__main__":
    toJSONFilter(cvss)
