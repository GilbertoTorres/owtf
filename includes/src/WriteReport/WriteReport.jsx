import React from 'react';
import { Button } from 'antd';
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
            errorData: []
        };
    }

    getInitialState() {
        return {
            code: '// Code'
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
            <Button type="primary" icon="download" size={'default'} onClick={this.download.bind(this, this.state.code, 'html')}>Download Html</Button>
            <Button type="primary" icon="download" size={'default'} onClick={this.download.bind(this, this.state.code, 'pdf')}>Download Pdf</Button>
            <Button type="primary" icon="download" size={'default'} onClick={this.download.bind(this, this.state.code, 'odt')}>Download Odt</Button>
            <Button type="primary" icon="save" onClick={this.save.bind(this, this.state.code)}>Save</Button>
            <CodeMirror value={this.state.code} onChange={this.updateCode.bind(this)} options={options} />
            </div>
        );
    }
}

export default WriteReport;
