import React from 'react';
import { Radio, Button } from 'antd';
const RadioButton = Radio.Button;
const RadioGroup = Radio.Group;
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

    save(content) {
        fetch(`/api/write_report/1`, {
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content
            })
          }).then((response) => response.json())
    };

    init() {
        fetch(`/api/write_report/1`, {
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
                <Button type="primary" icon="save" onClick={this.save.bind(this, this.state.code)}>Save</Button>
                <CodeMirror value={this.state.code} onChange={this.updateCode.bind(this)} options={options} />
            </div>
        );
    }
}

export default WriteReport;
