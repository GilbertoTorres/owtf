import React from 'react';
import Modal from 'react-modal';
import {TARGET_API_URI, REPORT_API_URI} from '../constants.jsx';

/**
  * React Component for Table in collapse. It is child component used by Collapse Component.
  */

const customStyles = {
  content : {
    top                   : '50%',
    left                  : '50%',
    right                 : 'auto',
    bottom                : 'auto',
    marginRight           : '-50%',
    transform             : 'translate(-50%, -50%)'
  }
};

class Table extends React.PureComponent {

  /**
    * Function responsible for handling editing of notes.
    * Uses REST API - /api/targets/<target_id>/poutput/<group>/<type>/<code>/
    * @param {group, type, code, user_rank} values group:group of plugin clicked, type: type of plugin clicked, code: code of plugin clicked, user_rank: rank changed to.
    */

    constructor() {
        super();

        this.state = {
          modalIsOpen: false,
          modalData: ""
        };

        this.openModal = this.openModal.bind(this);
        this.afterOpenModal = this.afterOpenModal.bind(this);
        this.closeModal = this.closeModal.bind(this);
    }

    patchUserNotes(group, type, code, user_notes) {
        var target_id = document.getElementById("report").getAttribute("data-code");
        var alert = this.context.alert;
        $.ajax({
            url: TARGET_API_URI + target_id + '/poutput/' + group + '/' + type + '/' + code,
            type: 'PATCH',
            data: {
                "user_notes": user_notes
            },
            error: function(xhr, textStatus, serverResponse) {
                alert.call(this, "Server replied: " + serverResponse);
            }.bind(this)
        });
    };

    openModal(type, id) {
        var apiUrl;
        if (type == "command") {
            apiUrl = REPORT_API_URI + "commands/" + id + "/hosts/"
        } else if (type == "plugin_output") {
            apiUrl = REPORT_API_URI + "plugin_outputs/" + id + "/hosts/"
        } else if (type == "target") {
            apiUrl = REPORT_API_URI + "targets/" + id + "/hosts/"
        }
        fetch(apiUrl)
          .then((data) => {
            // Here you get the data to modify as you please
                this.setState({modalIsOpen: true, modalData: data});
            })
    }

    afterOpenModal() {
        // references are now sync'd and can be accessed.
        this.subtitle.style.color = '#f00';
    }

    closeModal() {
        this.setState({modalIsOpen: false});
    }

    /**
      * Function responsible for handling user_notes editor.
      * Uses external library: (js/ckeditor/ckeditor.js, js/ckeditor/adapters/jquery.js)
      * Uses REST API - /api/targets/<target_id>/poutput/<group>/<type>/<code>/ to fill the editor area with user_notes.
      * @param {group, type, code, user_rank} values group:group of plugin clicked, type: type of plugin clicked, code: code of plugin clicked, user_rank: rank changed to.
      */

    handleEditor(group, type, code, instance) { // Same function called both to create or close editor
        var target_id = document.getElementById("report").getAttribute("data-code");
        var editorRef = "editor_" + group + "_" + type + "_" + code;
        var instance = this.refs[editorRef];
        var editorArea = $(instance).closest('table').find('.editor');
        var patchUserNotes = this.patchUserNotes;
        try {
            var editor = editorArea.ckeditorGet(); // This line generates error if editor not found
            patchUserNotes.call(this, group, type, code, editorArea.val());
            editor.destroy();
            editorArea.css("display", "None");
        } catch (err) {
            $.getJSON(TARGET_API_URI + target_id + '/poutput/' + group + '/' + type + '/' + code, function(data) {
                editorArea.val(data.user_notes);
                editorArea.ckeditor();
            });
        }
    };

    render() {
        var obj = this.props.obj;
        var output_path = encodeURIComponent(obj.output_path) + "/";
        var status = obj.status;
        var run_time = obj.run_time;
        var start_time = obj.start_time;
        var end_time = obj.end_time;
        var run_time = obj.status;
        var output = obj.output === undefined ? "" : obj.output;
        var group = obj.plugin.group;
        var type = obj.plugin.type;
        var code = obj.plugin.code;
        var commands = obj.commands;

        var deletePluginOutput = this.context.deletePluginOutput;
        var postToWorkList = this.context.postToWorkList;



        return (
            <div>
                <Modal
                  isOpen={this.state.modalIsOpen}
                  onAfterOpen={this.afterOpenModal}
                  onRequestClose={this.closeModal}
                  style={customStyles}
                  contentLabel="Example Modal"
                >

                  <h2 ref={subtitle => this.subtitle = subtitle}>Hello</h2>
                  <button onClick={this.closeModal}>close</button>
                  <div>I am a modal</div>
                  <form>
                    <input />
                    <button>tab navigation</button>
                    <button>stays</button>
                    <button>inside</button>
                    <button>the modal</button>
                  </form>
                </Modal>
                <table className="table table-bordered table-striped table-hover table-report">
                    <thead>
                        <tr>
                            <th>
                                RUNTIME
                            </th>
                            <th>
                                TIME INTERVAL
                            </th>
                            <th>
                                STATUS
                            </th>
                            {(() => {
                                if (output_path !== undefined) {
                                    return (
                                        <th>
                                            OUTPUT FILES
                                        </th>
                                    );
                                }
                            })()}
                            <th>
                                ACTIONS
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr className={(() => {
                            switch (status) {
                                case "Aborted":
                                    return "alert alert-warning";
                                case "Successful":
                                    return "alert alert-success";
                                case "Crashed":
                                    return "alert alert-error";
                                case "Running":
                                    return "alert alert-info";
                                case "Skipped":
                                    return "muted";
                                default:
                                    return "";
                            }
                        })()}>
                            <td>
                                {run_time}
                            </td>
                            <td>
                                {start_time}
                                <br/>{end_time}
                            </td>
                            <td>
                                {status}
                            </td>
                            {(() => {
                                if (output_path !== undefined) {
                                    return (
                                        <td>
                                            <a href={"/output_files/" + output_path} target="_blank" className={output_path === null ? "btn btn-primary disabled":"btn btn-primary"}>Browse</a>
                                        </td>
                                    );
                                }
                            })()}
                            <td>
                                <div className="btn-group">
                                    <button className="btn btn-success" onClick={postToWorkList.bind(this, {
                                        "code": code,
                                        "group": group,
                                        "type": type
                                    }, true)} data-toggle="tooltip" data-placement="bottom" title="Rerun plugin">
                                        <i className="fa fa-refresh"></i>
                                    </button>
                                    <button className="btn btn-danger" onClick={deletePluginOutput.bind(this, group, type, code, )} data-toggle="tooltip" data-placement="bottom" title="Delete plugin output">
                                        <i className="fa fa-times"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <th colSpan="6">
                                <button ref={"editor_" + group + "_" + type + "_" + code} className="btn btn-default pull-right" onClick={this.handleEditor.bind(this, group, type, code)}>
                                    <i className="fa fa-pencil"></i>
                                    Notes
                                </button>
                            </th>
                        </tr>
                        <tr>
                            <td colSpan="6">
                                <textarea className="editor" style={{
                                    display: "none"
                                }}></textarea>
                            </td>
                        </tr>
                        <tr>
                            <td colSpan="6">
                                <div className="btn-group btn-group-sm" role="group">
                                      <button className="btn btn-unranked" type="button"  onClick={this.openModal.bind(this,"plugin_output", obj.id)} >Hosts: {obj.hosts.length}</button>
                                      <button className="btn btn-unranked" type="button" disabled="disabled" >Ifaces: {obj.ifaces.length}</button>
                                      <button className="btn btn-unranked" type="button" disabled="disabled" >Services: {obj.services.length}</button>
                                      <button className="btn btn-unranked" type="button" disabled="disabled" >Creds: {obj.creds.length}</button>
                                      <button className="btn btn-unranked" type="button" >Vulns: {obj.vulns.length}</button>
                                      <button className="btn btn-unranked" type="button" disabled="disabled" >Notes: {'X'}</button>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <th colSpan="6">
                                COMMANDS
                            </th>
                        </tr>
                        {commands.map((cmd, i) => {
                                return (

                        <tr>
                        <td colSpan="6">
                            <div className="row-fluid">
                                <h4>Test Command</h4>
                                <div className="col-md-12">
                                    <pre className="commandPre">{cmd.original_command}</pre>
                                </div>
                            </div>
                            <div className="row-fluid">
                                <h4><a href="/output_files/{{ FilePath }}" target="_blank">{cmd.name}</a> Output (Execution Time: {cmd.start_time} - {cmd.end_time})</h4>
                                <div className="col-md-12">
                                    <pre className="wrappedPre">{cmd.small_stdout}</pre>
                                </div>
                            </div>
                            <div className="row-fluid">
                                 {/*{% if longOutput %}

                                 <div className='alert alert-warning'>
                                        <strong>NOTE!</strong>
                                        Output longer than {{ mNumLinesToShow }} lines,
                                        <a href="/output_files/{{ FilePath }}" target="_blank"> Click here to see all output! </a>
                                 </div>

                                 {% end %}*/}
                            </div>
                            {(() => {
                            if (cmd.normalized === true) {
                                return (
                                    <div className="btn-group btn-group-xs" role="group">
                                        <button className="btn btn-unranked" type="button" onClick={this.openModal.bind(this,"command", cmd.id)}>Hosts: {cmd.hosts.length}</button>
                                        <button className="btn btn-unranked" type="button" disabled="disabled" >Ifaces: {cmd.ifaces.length}</button>
                                        <button className="btn btn-unranked" type="button" disabled="disabled" >Services: {cmd.services.length}</button>
                                        <button className="btn btn-unranked" type="button" disabled="disabled" >Creds: {cmd.creds.length}</button>
                                        <button className="btn btn-unranked" type="button" >Vulns: {cmd.vulns.length}</button>
                                        <button className="btn btn-unranked" type="button" disabled="disabled" >Notes: {cmd.notes.length}</button>
                                    </div>
                                );
                            }
                            })()}
                        </td>
                        
                        </tr>
                                );
                        })}
                        <tr>
                            <th colSpan="6">
                                MORE DETAILS
                            </th>
                        </tr>
                        <tr>
                            <td colSpan="6" dangerouslySetInnerHTML={{
                                __html: output
                            }}></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        );
    }
}

Table.contextTypes = {
    deletePluginOutput: React.PropTypes.func,
    postToWorkList: React.PropTypes.func,
    alert: React.PropTypes.func
};

export default Table;
