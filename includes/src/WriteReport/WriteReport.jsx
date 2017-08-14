import _ from 'lodash'
import { Popconfirm, message, Input, Col, Row, Card, Radio, Button } from 'antd';
const RadioButton = Radio.Button;
const RadioGroup = Radio.Group;

import {
  BrowserRouter as Router,
  Route,
  Link
} from 'react-router-dom'
import { withRouter } from 'react-router'
import React from 'react';

import 'inline-attachment/src/inline-attachment'
import 'inline-attachment/src/codemirror-4.inline-attachment'
import 'codemirror/addon/dialog/dialog';
import 'codemirror/addon/dialog/dialog';
import 'codemirror/addon/search/search';
import 'codemirror/addon/search/searchcursor';
import 'codemirror/addon/search/jump-to-line';
import CodeMirror from 'react-codemirror';
import 'codemirror/mode/markdown/markdown';


const ReportInitLogic = ({reportId, onSuccess, run}) => {
  if (run) {
    fetch(`/api/write_reports/${reportId}`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
      }).then((response) => response.json())
      .then((responseJson) => {
        onSuccess({ 
              code: responseJson.content,
              title: responseJson.title 
        })
      })
  }
  return null;
}

class NewReportButton extends React.Component {

    constructor(props) {
        super(props);
    }

    createAndEdit() {
        fetch(`/api/write_reports/`, {
            method: 'POST',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: ''
            })
          }).then((response) => response.json())
            .then((responseJson) => {
                this.props.history.push(`/ui/write_reports/${responseJson.id}`)
          })
    }

    render() {
      return (
            <Button
            onClick={this.createAndEdit.bind(this)}>
            New Report
          </Button>
      )
    }
}
const NewReportButtonWithRouter = withRouter(NewReportButton)



class Index extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            reports: []
        };
    }


    componentDidMount() {

        fetch(`/api/write_reports/`, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            }
        }).then((response) => response.json())
          .then((responseJson) => {
            this.setState(
            { 
                reports: responseJson
            });
        })
    }

    renderRow(row, idx) {
        return <Row key={"report-col-" + idx.toString()}>{row.map(this.renderItem.bind(this))}</Row>;
    }

    deleteReport(id, e) {
        
        console.log(e);
        message.success('Delete confirmed!'); // FIXME: if not called twice, it did not appear
        message.success('Delete confirmed!');

        fetch(`/api/write_reports/${id}`, {
            method: 'DELETE',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            }
        }).then((response) => {
            var reports = _.filter(this.state.reports, function(r) {
              return r.id != id;
            })
            this.setState(
            { 
                reports: reports
            });
        })
    }

    cancel(e) {
      console.log(e);
      message.success('Delete canceled!'); // FIXME: if not called twice, it did not appear
      message.success('Delete canceled!');
    }

    renderItem(item) {
        return (
            <Col key={"report-col-" + item.id.toString()} span={6} xs={24} sm={12} md={6}>
                  <Card title={'Report "' + item.title + '"' } extra={''} style={{ width: 300 }}>
                    <p>{'Created At: ' + item.created_at + '' }</p>
                    <p>{'Updated At: ' + item.updated_at + '' }</p>
                    <p>
                    <Popconfirm title="Are you sure delete this report?" onConfirm={this.deleteReport.bind(this, item.id)} onCancel={this.cancel} okText="Yes" cancelText="No">
                      <Button type="danger" icon="delete">Delete</Button>
                    </Popconfirm>
                    <Button type="default" icon="edit"><Link to={'/ui/write_reports/' + item.id}>Edit</Link></Button>
                    </p>
                    
                  </Card>
              </Col>
              )
    }

    render() {

        var groups = _.chunk(this.state.reports, 4)
        return (
        <div>
            {groups.map(this.renderRow.bind(this))}
        </div>
        );
    }
}


class WriteReport extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            errorData: [],
            code: '// Code',
            title: '',
            selectedFormat: 'pdf',
            currentReportId: this.props.match.params.id,
            doInitReport: true
        };
    }

    componentDidMount() {
        this.init();
    }

    componentWillReceiveProps(nextProps) {
        if (this.props.match.params.id != nextProps.match.params.id) {
            this.setState(
            { 
                doInitReport: true
            })
        } else {
            console.log("Same ids ...");
        }
    }

    updateCode(newCode) {
        this.setState(
            { 
                code: newCode 
            })
    };

    updateTitle(event) {
        this.setState(
            { 
                title: event.target.value 
            })
    };

    onFormatChange(e) {
        this.setState({
          selectedFormat: e.target.value,
        })
      }

    download(content, format) {
        fetch(`/api/write_reports/export/?format=`+format, {
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
            window.location = '/api/write_reports/download?file='+responseJson.file + '&format='+format
          })
    };

    save() {
        const reportId = this.props.match.params.id
        fetch(`/api/write_reports/${reportId}`, {
            method: 'PUT',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: this.state.code,
                title: this.state.title
            })
          })
    };

    init() {

      inlineAttachment.editors.codemirror4.attach(
        this.myCodeMirror.getCodeMirror(),
        {
          uploadUrl: `/api/write_reports/${this.state.currentReportId}/upload-attachment`
        }
      )
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
                <Button type="primary" icon="save" onClick={this.save.bind(this)}>Save</Button>
                <Input placeholder="Report Title" value={this.state.title} onChange={this.updateTitle.bind(this)} />
                <CodeMirror ref={(ref) => this.myCodeMirror = ref} value={this.state.code} onChange={this.updateCode.bind(this)} options={options} />
                <ReportInitLogic run={this.state.doInitReport} 
                            reportId={this.state.currentReportId} 
                            onSuccess={(state) => { this.setState({ title: state.title, code: state.code, doInitReport: false}) } } 
                          />
            </div>
        );
    }
}

const WriteReportRouter = () => (
  <Router>
    <div>
      <NewReportButtonWithRouter/>
      <Route exact path="/ui/write_reports/" component={Index}/>
      <Route path="/ui/write_reports/:id" component={WriteReport}/>
    </div>
  </Router>
)

export default WriteReportRouter;
