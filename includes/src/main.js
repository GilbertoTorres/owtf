import React from 'react';
import ReactDOM from 'react-dom';
import Home from './Home/Home.jsx';
import Dashboard from './Dashboard/Dashboard.jsx';
import Transactions from './Transactions/Transactions.jsx';
import Report from './Report/Report.jsx';
import WriteReport from './WriteReport/WriteReport.jsx';

var pageID = document.getElementById('app').childNodes[1].id;

if ( pageID == 'home') {
  ReactDOM.render(<Home />, document.getElementById('home'));
} else if ( pageID == 'dashboard') {
  ReactDOM.render(<Dashboard />, document.getElementById('dashboard'));
} else if ( pageID == 'transactions') {
  ReactDOM.render(<Transactions />, document.getElementById('transactions'));
} else if ( pageID == 'write_report') {
  ReactDOM.render(<WriteReport />, document.getElementById('write_report'));
} else if ( pageID == 'report') {
  ReactDOM.render(<Report />, document.getElementById('report'));
}
