import React from 'react';
import {REPORT_API_URI} from '../constants.jsx';
import {Pie} from 'react-chartjs';
import ReactTable from 'react-table'
import TreeView from 'react-treeview'
import Modal from 'react-modal'

export class VulnerabilityCountPieChart extends React.PureComponent {

  /**
    * Function responsible for handling editing of notes.
    * Uses REST API - /api/targets/<target_id>/poutput/<group>/<type>/<code>/
    * @param {group, type, code, user_rank} values group:group of plugin clicked, type: type of plugin clicked, code: code of plugin clicked, user_rank: rank changed to.
    */

    constructor(props) {
        super(props);

        this.state = {
          pieData: null
        };
    }

    componentDidMount() {

        var apiUrl;
        if (this.props.objType == "command") {
            apiUrl = REPORT_API_URI + "commands/" + this.props.objId + "/hosts/"
        } else if (this.props.objType == "plugin_output") {
            apiUrl = REPORT_API_URI + "plugin_outputs/" + this.props.objId + "/hosts/"
        } else if (this.props.objType == "target") {
            apiUrl = REPORT_API_URI + "targets/" + this.props.objId + "/hosts/"
        }

        fetch(apiUrl)
          .then((response) => response.json())
          .then((data) => {
            console.log("data is:", data);

            var severity = data.stats.vulnerabilities.severity;
            var pieData;
            if ((severity.passing + 
                    severity.info + 
                        severity.low + 
                        severity.medium + 
                        severity.high + 
                        severity.critical) == 0) {
                
                pieData = [
                  {
                    color: "blue",
                    id: 0,
                    value: 1,
                    label: "No vulnerabilities found"
                  }
                ];
            } else {
                pieData = [
                  {
                    color: "#32CD32",
                    id: 0,
                    value: severity.passing,
                    label: "Passing"
                  },
                  {
                    color: "#b1d9f4",
                    id: 1,
                    value: severity.info,
                    label: "Info"
                  },
                  {
                    color: "#337ab7",
                    id: 2,
                    value: severity.low,
                    label: "Low"
                  },
                  {
                    color: "#ffcc00",
                    id: 3,
                    value: severity.medium,
                    label: "Medium"
                  },
                  {
                    color: "#c12e2a",
                    id: 4,
                    value: severity.high,
                    label: "High"
                  },
                  {
                    color: "#800080",
                    id: 5,
                    value: severity.critical,
                    label: "Critical"
                  }
                ];
            }


            this.setState({pieData: pieData});
          })
    }

    render() {
        return (
            <div>
                <Pie data={this.state.pieData} width="175%" height="175%"/>
            </div>
        );
    }
}

export class HostsEnhancementTable extends React.PureComponent {

  /**
    * Function responsible for handling editing of notes.
    * Uses REST API - /api/targets/<target_id>/poutput/<group>/<type>/<code>/
    * @param {group, type, code, user_rank} values group:group of plugin clicked, type: type of plugin clicked, code: code of plugin clicked, user_rank: rank changed to.
    */

    constructor(props) {
        super(props);

        this.state = {
          data: []
        };
    }

    componentDidMount() {
        
        var apiUrl;
        if (this.props.objType == "command") {
            apiUrl = REPORT_API_URI + "commands/" + this.props.objId + "/hosts/"
        } else if (this.props.objType == "plugin_output") {
            apiUrl = REPORT_API_URI + "plugin_outputs/" + this.props.objId + "/hosts/"
        } else if (this.props.objType == "target") {
            apiUrl = REPORT_API_URI + "targets/" + this.props.objId + "/hosts/"
        }

        fetch('/api/report/commands/12/table/vulns')
          .then((response) => response.json())
          .then((data) => {
            this.setState({data: data.objs});
          })

    }

    render() {

      const columns = [{
        Header: 'Name',
        accessor: 'name' // String-based value accessors!
      }, {
        Header: 'Severity',
        accessor: 'severity',
        Cell: props => <span className='number'>{props.value}</span> // Custom cell components!
      }, {
        Header: 'Count', // Custom header components!
        accessor: 'count'
      }]

      return (
            <ReactTable
                data={this.state.data}
                columns={columns}
                defaultPageSize={5}
                showPageSizeOptions={false}
                />
        )
    }

}

export class ServicesEnhancementTable extends React.PureComponent {

  /**
    * Function responsible for handling editing of notes.
    * Uses REST API - /api/targets/<target_id>/poutput/<group>/<type>/<code>/
    * @param {group, type, code, user_rank} values group:group of plugin clicked, type: type of plugin clicked, code: code of plugin clicked, user_rank: rank changed to.
    */

    constructor(props) {
        super(props);

        this.state = {
          data: []
        };
    }

    componentDidMount() {
        
        var apiUrl;
        if (this.props.objType == "command") {
            apiUrl = REPORT_API_URI + "commands/" + this.props.objId + "/hosts/"
        } else if (this.props.objType == "plugin_output") {
            apiUrl = REPORT_API_URI + "plugin_outputs/" + this.props.objId + "/hosts/"
        } else if (this.props.objType == "target") {
            apiUrl = REPORT_API_URI + "targets/" + this.props.objId + "/hosts/"
        }

        fetch('/api/report/commands/12/table/vulns')
          .then((response) => response.json())
          .then((data) => {
            this.setState({data: data.objs});
          })

    }

    render() {

      const columns = [{
        Header: 'Name',
        accessor: 'name' // String-based value accessors!
      }, {
        Header: 'Severity',
        accessor: 'severity',
        Cell: props => <span className='number'>{props.value}</span> // Custom cell components!
      }, {
        Header: 'Count', // Custom header components!
        accessor: 'count'
      }]

      return (
            <ReactTable
                data={this.state.data}
                columns={columns}
                defaultPageSize={5}
                showPageSizeOptions={false}
                />
        )
    }

}

export class VulnsEnhancementTable extends React.PureComponent {

  /**
    * Function responsible for handling editing of notes.
    * Uses REST API - /api/targets/<target_id>/poutput/<group>/<type>/<code>/
    * @param {group, type, code, user_rank} values group:group of plugin clicked, type: type of plugin clicked, code: code of plugin clicked, user_rank: rank changed to.
    */

    constructor(props) {
        super(props);

        this.state = {
          data: []
        };
    }

    componentDidMount() {
        
        var apiUrl;
        if (this.props.objType == "command") {
            apiUrl = REPORT_API_URI + "commands/" + this.props.objId + "/hosts/"
        } else if (this.props.objType == "plugin_output") {
            apiUrl = REPORT_API_URI + "plugin_outputs/" + this.props.objId + "/hosts/"
        } else if (this.props.objType == "target") {
            apiUrl = REPORT_API_URI + "targets/" + this.props.objId + "/hosts/"
        }

        fetch('/api/report/commands/12/table/vulns')
          .then((response) => response.json())
          .then((data) => {
            this.setState({data: data.objs});
          })

    }

    render() {

      const columns = [{
        Header: 'Name',
        accessor: 'name' // String-based value accessors!
      }, {
        Header: 'Severity',
        accessor: 'severity',
        Cell: props => <span className='number'>{props.value}</span> // Custom cell components!
      }, {
        Header: 'Count', // Custom header components!
        accessor: 'count'
      }]

      return (
            <ReactTable
                data={this.state.data}
                columns={columns}
                defaultPageSize={5}
                showPageSizeOptions={false}
                />
        )
    }

}

export class CredsEnhancementTable extends React.PureComponent {

  /**
    * Function responsible for handling editing of notes.
    * Uses REST API - /api/targets/<target_id>/poutput/<group>/<type>/<code>/
    * @param {group, type, code, user_rank} values group:group of plugin clicked, type: type of plugin clicked, code: code of plugin clicked, user_rank: rank changed to.
    */

    constructor(props) {
        super(props);

        this.state = {
          data: []
        };
    }

    componentDidMount() {
        
        var apiUrl;
        if (this.props.objType == "command") {
            apiUrl = REPORT_API_URI + "commands/" + this.props.objId + "/hosts/"
        } else if (this.props.objType == "plugin_output") {
            apiUrl = REPORT_API_URI + "plugin_outputs/" + this.props.objId + "/hosts/"
        } else if (this.props.objType == "target") {
            apiUrl = REPORT_API_URI + "targets/" + this.props.objId + "/hosts/"
        }

        fetch('/api/report/commands/12/table/vulns')
          .then((response) => response.json())
          .then((data) => {
            this.setState({data: data.objs});
          })

    }

    render() {

      const columns = [{
        Header: 'Name',
        accessor: 'name' // String-based value accessors!
      }, {
        Header: 'Severity',
        accessor: 'severity',
        Cell: props => <span className='number'>{props.value}</span> // Custom cell components!
      }, {
        Header: 'Count', // Custom header components!
        accessor: 'count'
      }]

      return (
            <ReactTable
                data={this.state.data}
                columns={columns}
                defaultPageSize={5}
                showPageSizeOptions={false}
                />
        )
    }

}

export class NotesEnhancementTable extends React.PureComponent {

  /**
    * Function responsible for handling editing of notes.
    * Uses REST API - /api/targets/<target_id>/poutput/<group>/<type>/<code>/
    * @param {group, type, code, user_rank} values group:group of plugin clicked, type: type of plugin clicked, code: code of plugin clicked, user_rank: rank changed to.
    */

    constructor(props) {
        super(props);

        this.state = {
          data: []
        };
    }

    componentDidMount() {
        
        var apiUrl;
        if (this.props.objType == "command") {
            apiUrl = REPORT_API_URI + "commands/" + this.props.objId + "/hosts/"
        } else if (this.props.objType == "plugin_output") {
            apiUrl = REPORT_API_URI + "plugin_outputs/" + this.props.objId + "/hosts/"
        } else if (this.props.objType == "target") {
            apiUrl = REPORT_API_URI + "targets/" + this.props.objId + "/hosts/"
        }

        fetch('/api/report/commands/12/table/vulns')
          .then((response) => response.json())
          .then((data) => {
            this.setState({data: data.objs});
          })

    }

    render() {

      const columns = [{
        Header: 'Name',
        accessor: 'name' // String-based value accessors!
      }, {
        Header: 'Severity',
        accessor: 'severity',
        Cell: props => <span className='number'>{props.value}</span> // Custom cell components!
      }, {
        Header: 'Count', // Custom header components!
        accessor: 'count'
      }]

      return (
            <ReactTable
                data={this.state.data}
                columns={columns}
                defaultPageSize={5}
                showPageSizeOptions={false}
                />
        )
    }
}


export class ReportEnhancementModal extends React.PureComponent {

  /**
    * Function responsible for handling editing of notes.
    * Uses REST API - /api/targets/<target_id>/poutput/<group>/<type>/<code>/
    * @param {group, type, code, user_rank} values group:group of plugin clicked, type: type of plugin clicked, code: code of plugin clicked, user_rank: rank changed to.
    */

    constructor(props) {
        super(props);
        this.state = {
          modalIsOpen: false
        };

        this.closeModal = this.closeModal.bind(this);
        this.afterOpenModal = this.afterOpenModal.bind(this);
    }

    componentWillReceiveProps(nextProps) {
      // You don't have to do this check first, but it can help prevent an unneeded render
      if (nextProps.modalIsOpen !== this.state.modalIsOpen) {
        console.log("Setting state")
        this.setState({ modalIsOpen: nextProps.modalIsOpen });
      }
    }

    afterOpenModal() {
        // references are now sync'd and can be accessed.
        this.subtitle.style.color = '#000';
    }

    closeModal() {
        this.setState({modalIsOpen: false});
    }

    render() {

        var obj = this.props.obj;
        const customStyles = {
          content : {
            top                   : '50%',
            left                  : '50%',
            right                 : 'auto',
            bottom                : 'auto',
            marginRight           : '-50%',
            transform             : 'translate(-50%, -50%)',
            height: '80%', // <-- This sets the height
            width: '80%', // <-- This sets the height
            overlfow: 'scroll' // <-- This tells the modal to scrol
          }
        };
      
        return (
                <Modal
                  isOpen={this.state.modalIsOpen}
                  onAfterOpen={this.afterOpenModal}
                  onRequestClose={this.closeModal}
                  style={customStyles}
                  contentLabel="Example Modal"
                >
                  <h2 ref={subtitle => this.subtitle = subtitle}>Findings Report OWTF</h2>
                  <button onClick={this.closeModal}>close</button>
                    <div className="row-fluid">
                        <div className="col-md-6">
                            <h5>Hosts</h5>
                            <HostsEnhancementTable objId={this.props.objId} objType={this.props.objType} />
                        </div>
                        <div className="col-md-6">
                            <h5>Services</h5>
                            <ServicesEnhancementTable objId={this.props.objId} objType={this.props.objType} />
                        </div>
                    </div>                                      
                    <div className="row-fluid">
                        <h4>Vulnerabilities</h4>
                        <div className="col-md-6">
                            <h5>Vulnerabilities by severity</h5>
                            <VulnerabilityCountPieChart objId={this.props.objId} objType={this.props.objType} />
                        </div>
                        <div className="col-md-6">
                            <h5>Vulnerabilities</h5>
                            <VulnsEnhancementTable objId={this.props.objId} objType={this.props.objType} />
                        </div>
                    </div>                    
                    <div className="row-fluid">
                        <div className="col-md-6">
                            <h5>Notes</h5>
                            <NotesEnhancementTable objId={this.props.objId} objType={this.props.objType} />
                        </div>
                        <div className="col-md-6">
                        </div>
                    </div>                    
                </Modal>
        )
    }

}
