import React from 'react';
import {REPORT_API_URI} from '../constants.jsx';
import {Doughnut} from 'react-chartjs';
import ReactTable from 'react-table'
import TreeView from 'react-treeview'
import Modal from 'react-modal'


function vulnSeveritiesApiUrlFor(id, type, entity) {
    
    var apiUrl
    if (type == "command") {
        apiUrl = REPORT_API_URI + "commands/" + id + "/vulns/severity"
    } else if (type == "plugin_output") {
        apiUrl = REPORT_API_URI + "plugin_outputs/" + id + "/vulns/severity"
    } else if (type == "target") {
        apiUrl = REPORT_API_URI + "targets/" + id + "/vulns/severity"
    } else if (type == "session") {
        apiUrl = REPORT_API_URI + "current_session/vulns/severity"
    }
    return apiUrl
}

function tableApiUrlFor(id, type, entity) {
    
    var apiUrl
    if (type == "command") {
        apiUrl = REPORT_API_URI + "commands/" + id + "/table/" + entity + ""
    } else if (type == "plugin_output") {
        apiUrl = REPORT_API_URI + "plugin_outputs/" + id + "/table/" + entity + ""
    } else if (type == "target") {
        apiUrl = REPORT_API_URI + "targets/" + id + "/table/" + entity + ""
    } else if (type == "session") {
        apiUrl = REPORT_API_URI + "current_session/table/" + entity + ""
    }
    return apiUrl
}

function badgeApiUrlFor(id, type) {
    
    var apiUrl
    if (type == "command") {
        apiUrl = REPORT_API_URI + "commands/" + id + "/badge"
    } else if (type == "plugin_output") {
        apiUrl = REPORT_API_URI + "plugin_outputs/" + id + "/badge"
    } else if (type == "target") {
        apiUrl = REPORT_API_URI + "targets/" + id + "/badge"
    } else if (type == "session") {
        apiUrl = REPORT_API_URI + "current_session/badge"
    }
    return apiUrl
}

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

        var apiUrl = vulnSeveritiesApiUrlFor(this.props.objId, this.props.objType, "hosts")

        fetch(apiUrl)
          .then((response) => response.json())
          .then((data) => {
            var severities = data.severities;
            var pieData;
            if ((severities.passing + 
                    severities.info + 
                        severities.low + 
                        severities.medium + 
                        severities.high + 
                        severities.critical) == 0) {
                
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
                    value: severities.passing,
                    label: "Passing"
                  },
                  {
                    color: "#b1d9f4",
                    id: 1,
                    value: severities.info,
                    label: "Info"
                  },
                  {
                    color: "#337ab7",
                    id: 2,
                    value: severities.low,
                    label: "Low"
                  },
                  {
                    color: "#ffcc00",
                    id: 3,
                    value: severities.medium,
                    label: "Medium"
                  },
                  {
                    color: "#c12e2a",
                    id: 4,
                    value: severities.high,
                    label: "High"
                  },
                  {
                    color: "#800080",
                    id: 5,
                    value: severities.critical,
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
                <Doughnut data={this.state.pieData} width="175%" height="175%"/>
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
          dataSource: []
        };
    }

    componentDidMount() {
        
        var apiUrl = tableApiUrlFor(this.props.objId, this.props.objType, "hosts")

        fetch(apiUrl)
          .then((response) => response.json())
          .then((data) => {
            this.setState({dataSource: data.objs});
          })

    }

    render() {

      const columns = [{
        Header: 'Name',
        accessor: 'name' // String-based value accessors!
      }, {
        Header: 'OS',
        accessor: 'os'
      }, {
        Header: 'Count', // Custom header components!
        accessor: 'count'
      }]

      return (
            <ReactTable
                data={this.state.dataSource}
                columns={columns}
                defaultPageSize={5}
                showPageSizeOptions={false}
                className="-striped -highlight"
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
          dataSource: []
        };
    }

    componentDidMount() {
        
        var apiUrl = tableApiUrlFor(this.props.objId, this.props.objType, "services")

        fetch(apiUrl)
          .then((response) => response.json())
          .then((data) => {
            this.setState({dataSource: data.objs});
          })

    }

    render() {

      const columns = [{
        Header: 'Name',
        accessor: 'name' // String-based value accessors!
      }, {
        Header: 'Ports',
        accessor: 'ports',
        Cell: props => <span className='number'>{props.value}</span> // Custom cell components!
      }, {
        Header: 'Protocol', // Custom header components!
        accessor: 'protocol'
      }, {
        Header: 'Version', // Custom header components!
        accessor: 'version'
      }, {
        Header: 'Host', // Custom header components!
        accessor: 'host'
      }]

      return (
            <ReactTable
                data={this.state.dataSource}
                columns={columns}
                defaultPageSize={5}
                showPageSizeOptions={false}
                className="-striped -highlight"
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
          dataSource: []
        };
    }

    componentDidMount() {
        
        var apiUrl = tableApiUrlFor(this.props.objId, this.props.objType, "vulns")

        fetch(apiUrl)
          .then((response) => response.json())
          .then((data) => {
            this.setState({dataSource: data.objs});
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
                data={this.state.dataSource}
                columns={columns}
                defaultPageSize={5}
                showPageSizeOptions={false}
                className="-striped -highlight"
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
          dataSource: []
        };
    }

    componentDidMount() {
        
        var apiUrl = tableApiUrlFor(this.props.objId, this.props.objType, "creds")

        fetch(apiUrl)
          .then((response) => response.json())
          .then((data) => {
            this.setState({dataSource: data.objs});
          })

    }

    render() {

      const columns = [{
        Header: 'Username',
        accessor: 'username' // String-based value accessors!
      }, {
        Header: 'Password',
        accessor: 'password',
        Cell: props => <span className='number'>{props.value}</span> // Custom cell components!
      }]

      return (
            <ReactTable
                data={this.state.dataSource}
                columns={columns}
                defaultPageSize={5}
                showPageSizeOptions={false}
                className="-striped -highlight"
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
          dataSource: []
        };
    }

    componentDidMount() {
        
        // var apiUrl = tableApiUrlFor(this.props.objId, this.props.objType, "notes")

        // fetch('/api/report/commands/12/table/vulns')
        //   .then((response) => response.json())
        //   .then((data) => {
        //     this.setState({dataSource: data.objs});
        //   })
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
                data={this.state.dataSource}
                columns={columns}
                defaultPageSize={5}
                showPageSizeOptions={false}
                className="-striped -highlight"
                />
        )
    }
}

export class ReportEnhancementBadge extends React.PureComponent {

  /**
    * Function responsible for handling editing of notes.
    * Uses REST API - /api/targets/<target_id>/poutput/<group>/<type>/<code>/
    * @param {group, type, code, user_rank} values group:group of plugin clicked, type: type of plugin clicked, code: code of plugin clicked, user_rank: rank changed to.
    */

    constructor(props) {
        super(props);

        this.state = {
          badgeCount: []
        };
    }

    componentDidMount() {
        
        var apiUrl = badgeApiUrlFor(this.props.objId, this.props.objType)

        fetch(apiUrl)
          .then((response) => response.json())
          .then((data) => {
            this.setState({badgeCount: data.badge});
          })
    }

    render() {
      return (
          <div className={"btn-group " + this.props.groupClass} role="group">
              <button className="btn btn-unranked" type="button" onClick={this.props.openModalHandler}><i className="fa fa-bar-chart"></i>Report</button>
              <button className="btn btn-unranked" type="button" disabled="disabled" >Hosts: {this.state.badgeCount.host_count}</button>
              <button className="btn btn-unranked" type="button" disabled="disabled" >Ifaces: {this.state.badgeCount.iface_count}</button>
              <button className="btn btn-unranked" type="button" disabled="disabled" >Services: {this.state.badgeCount.service_count}</button>
              <button className="btn btn-unranked" type="button" disabled="disabled" >Creds: {this.state.badgeCount.cred_count}</button>
              <button className="btn btn-unranked" type="button" disabled="disabled" >Vulns: {this.state.badgeCount.vuln_count}</button>
              <button className="btn btn-unranked" type="button" disabled="disabled" >Notes: {this.state.badgeCount.note_count}</button>
          </div>
        )
    }
}

ReportEnhancementBadge.defaultProps = {
  groupClass: "btn-group-xl",
  objId: -1 // session does not reseive an id, it's handled server-side
}

export class CommandsEnhancementTable extends React.PureComponent {

  /**
    * Function responsible for handling editing of notes.
    * Uses REST API - /api/targets/<target_id>/poutput/<group>/<type>/<code>/
    * @param {group, type, code, user_rank} values group:group of plugin clicked, type: type of plugin clicked, code: code of plugin clicked, user_rank: rank changed to.
    */

    constructor(props) {
        super(props);

        this.state = {
          dataSource: []
        };
    }

    componentDidMount() {
        
        var apiUrl = tableApiUrlFor(this.props.objId, this.props.objType, "commands")

        fetch(apiUrl)
          .then((response) => response.json())
          .then((data) => {
            this.setState({dataSource: data.objs});
          })
    }

    render() {
      const columns = [{
        Header: 'Name',
        accessor: 'name' // String-based value accessors!
      }, {
        Header: 'Command',
        accessor: 'original_command',
      }]


      return (
            <ReactTable
                data={this.state.dataSource}
                columns={columns}
                defaultPageSize={5}
                showPageSizeOptions={false}
                className="-striped -highlight"
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
                  <div className="text-center">
                    <h2 ref={subtitle => this.subtitle = subtitle}>Findings Report OWTF</h2>
                    <button onClick={this.closeModal}>close</button>
                  </div>
                    <div className="row-fluid">
                        <div className="col-md-2 col-md-offset-2">
                            <h5>Vulnerabilities by severity</h5>
                            <VulnerabilityCountPieChart objId={this.props.objId} objType={this.props.objType} />
                        </div>
                        <div className="col-md-offset-2 col-md-6">
                            <h5>Commands</h5>
                            <CommandsEnhancementTable objId={this.props.objId} objType={this.props.objType} />
                        </div>
                    </div>                                    
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
                        <div className="col-md-6">
                            <h5>Vulnerabilities</h5>
                            <VulnsEnhancementTable objId={this.props.objId} objType={this.props.objType} />
                        </div>
                        <div className="col-md-6">
                            <h5>Credentials</h5>
                            <CredsEnhancementTable objId={this.props.objId} objType={this.props.objType} />
                        </div>
                    </div>
                    <div className="row-fluid">
                        <div className="col-md-6">
                            <h5>Notes</h5>
                            <NotesEnhancementTable objId={this.props.objId} objType={this.props.objType} />
                        </div>
                    </div>
                </Modal>
        )
    }

}
