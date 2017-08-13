import React from 'react';
import { Radio, Button } from 'antd';
const RadioButton = Radio.Button;
const RadioGroup = Radio.Group;

import 'inline-attachment/src/inline-attachment'
import 'inline-attachment/src/codemirror-4.inline-attachment'
import 'codemirror/addon/dialog/dialog';
import 'codemirror/addon/dialog/dialog';
import 'codemirror/addon/search/search';
import 'codemirror/addon/search/searchcursor';
import 'codemirror/addon/search/jump-to-line';
import CodeMirror from 'react-codemirror';
import 'codemirror/mode/markdown/markdown';

class WriteReport extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            errorData: [],
            code: '// Code',
            selectedFormat: 'pdf'
        };
    }

    getInitialState() {
        return {
            code: '// Code',
            selectedFormat: 'pdf'
        };
    }

    componentDidMount() {
        this.init();
    }

    updateCode(newCode) {
        this.setState(
            { 
                code: newCode 
            });
    };

    onFormatChange(e) {
        console.log('radio checked', e.target.value);
        this.setState({
          selectedFormat: e.target.value,
        });
      }

    download(content, format) {
        fetch(`/api/write_report/export/?format=`+format, {
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content
            })
          }).then((response) => response.json())
            .then((responseJson) => {
            window.location = '/api/write_report/download?file='+responseJson.file + '&format='+format
          })
    };

    save(reportId, content) {
        fetch(`/api/write_report/${reportId}`, {
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content
            })
          })
    };

    init() {
        var reportId = document.getElementById('write_report').getAttribute('data-report-id');
        if (!reportId) {
            reportId = 1;
        }
        
        inlineAttachment.editors.codemirror4.attach(
            this.myCodeMirror.getCodeMirror(),
            {
                uploadUrl: `/api/write_report/${reportId}/upload-attachment`
            }
        );
        this.setState(
        { 
            reportId: reportId
        });
        fetch(`/api/write_report/${reportId}`, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            }
        }).then((response) => response.json())
            .then((responseJson) => {
                console.log("FOOO")
                this.setState(
                { 
                    code: responseJson.content 
                });
            })
    };

    render() {
        var options = {
            lineNumbers: true,
            lineWrapping: true,
            mode: 'markdown'
        };

        return (
            <div>
                <Button type="primary" icon="download" size={'default'} onClick={this.download.bind(this, this.state.code, this.state.selectedFormat)}>Download</Button>
                <RadioGroup defaultValue="pdf" onChange={this.onFormatChange.bind(this)} value={this.state.selectedFormat}>
                  <Radio value="pdf" checked={true}>pdf (latex)</Radio>
                  <Radio value="pdf2" disabled={true}>pdf (wkhtmltopdf)</Radio>
                  <Radio value="html">html</Radio>
                  <Radio value="odt">odt</Radio>
                </RadioGroup>
                <br/>
                <Button type="primary" icon="save" onClick={this.save.bind(this, this.state.reportId, this.state.code)}>Save</Button>
                <CodeMirror ref={(ref) => this.myCodeMirror = ref} value={this.state.code} onChange={this.updateCode.bind(this)} options={options} />
            </div>
        );
    }
}

export default WriteReport;
