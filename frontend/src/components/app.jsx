import React from 'react';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';

import AppBar from 'material-ui/AppBar';
import RaisedButton from 'material-ui/RaisedButton';


export default () => (
    <MuiThemeProvider>
      <div>
      <AppBar title="hello"/>
      <div>hello</div>
      <RaisedButton label="test"/>
      </div>
    </MuiThemeProvider>
);
