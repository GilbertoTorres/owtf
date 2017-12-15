import Docxtemplater from 'docxtemplater';
import {TARGET_API_URI} from '../constants.jsx';
import {importDirectory} from '../utils.js';
import JSZip from 'jszip';
import saveAs from 'save-as';
import expressions from 'angular-expressions'

const templates = importDirectory(require.context('./templates/', true, /\.(docx)$/));

export const templatesNames = Object.keys(templates);

// define your filter functions here, for example, to be able to write {clientname | lower}
expressions.filters.lower = function(input) {
    // This condition should be used to make sure that if your input is undefined, your output will be undefined as well and will not throw an error
    if(!input) return input;
    return input.toLowerCase();
}
var angularParser = function(tag) {
    return {
        get: tag === '.' ? function(s){ return s;} : function(s) {
            return expressions.compile(tag.replace(/’/g, "'"))(s);
        }
    };
}

// Funtion responsible for generating docx from JSON using docxtemplater.
function getDocxReportFromJSON(json, template) {
    var zip = new JSZip(templates[template]);
    var doc = new Docxtemplater();
    doc.loadZip(zip);

    //set the templateVariables
    doc.setData(json);
    doc.setOptions({parser:angularParser})

    try {
        // render the document (replace all occurences of tags.
        doc.render()
    } catch (error) {
        var e = {
            message: error.message,
            name: error.name,
            stack: error.stack,
            properties: error.properties
        }
        console.log(JSON.stringify({
            error: e
        }));
        // The error thrown here contains additional information when logged with JSON.stringify (it contains a property object).
        throw error;
    }

    var out = doc.getZip().generate({
        type: "blob",
        mimeType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    })
    saveAs(out, 'report.docx');
}

/**
  * Funtion to generate docx format.
  * Uses REST API - /api/targets/<target_id>/export/
  * docxtemplater takes a JSON and docx template and outputs output docx.
  */

export function getDocx(target_id, template) {
    $.ajax({
        url: TARGET_API_URI + target_id + '/export/',
        type: 'GET',
        success: function(result) {
            getDocxReportFromJSON(result, template);
        },
        error: function(xhr, textStatus, serverResponse) {
            console.log("Server replied: " + serverResponse);
        }
    });
}
