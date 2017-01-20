import React from 'react';
import Relay from 'react-relay';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';

import AppBar from 'material-ui/AppBar';
import RaisedButton from 'material-ui/RaisedButton';

export default () => (
    <MuiThemeProvider>
      <div>
      <AppBar title="hello"/>
      <div>hello</div>
      <p>N containers:</p>
      <RaisedButton label="test"/>
      </div>
    </MuiThemeProvider>
);
