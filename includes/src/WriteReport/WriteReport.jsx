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
            <Button type='primary' icon="save">Save</Button>
            <CodeMirror value={this.state.code} onChange={this.updateCode.bind(this)} options={options} />
            </div>
        );
    }
}

export default WriteReport;
