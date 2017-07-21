import React from 'react';
import { Button } from 'antd';
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

    updateCode(newCode) {
        this.setState(
            { 
                code: newCode 
            });
    };

    download() {
        fetch(`/api/write_report/export/`, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
          }).then((response) => response.json())
            .then((responseJson) => {
            var _format = 'html';
            window.location = 'http://127.0.0.1:8009/api/write_report/download?file='+responseJson.file + '&format='+_format
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
            <Button type="primary" icon="download" size={'default'} onClick={this.download.bind(this)}>Download</Button>
            <Button type='primary' icon="save">Save</Button>
            <CodeMirror value={this.state.code} onChange={this.updateCode.bind(this)} options={options} />
            </div>
        );
    }
}

export default WriteReport;
