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

echo "" > /tmp/input.md && \
	sed -e "s/—/---/g" -e "s/’/'/" $INFILE >> /tmp/input.md

iconv -c -f utf-8 -t utf-8 /tmp/input.md| php -R 'while(($$line=fgets(STDIN)) !== FALSE) echo html_entity_decode($$line, ENT_QUOTES|ENT_HTML401);' > $INFILE



COMMAND="$TOOL_BIN $INFILE --template $INFILE | $PANDOC_CMD"

echo "[*] Running: $COMMAND"

$TOOL_BIN $INFILE --template $INFILE | $PANDOC_CMD
