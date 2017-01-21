import React from 'react';
import Relay from 'react-relay';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import { Router, Route, hashHistory } from 'react-router'

import AppBar from 'material-ui/AppBar';

import CollectionsScreen from './collectionsscreen.jsx';
import css from './app.less';

export default (props) => (
  <MuiThemeProvider>
    <Router history={hashHistory}>
      <Route path='/' component={CollectionsScreen} />
    </Router>
  </MuiThemeProvider>
);
