#!/usr/bin/env bash
#
# Description:
#       Script to run wapiti with appropriate switches for basic and
#       time-efficient web app/web server vuln detection
#
# Date:    2014-08-09

TOOL_BIN=$1
INFILE=$2
PANDOC_CMD=$3

COMMAND="$TOOL_BIN $INFILE --template $INFILE | $PANDOC_CMD"

echo "[*] Running: $COMMAND"

$TOOL_BIN $INFILE --template $INFILE | $PANDOC_CMD
