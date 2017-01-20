import React from 'react';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';

import RaisedButton from 'material-ui/RaisedButton';


export default () => (
    <MuiThemeProvider>
      <div>
      <div>hello</div>
      <RaisedButton label="test"/>
      </div>
    </MuiThemeProvider>
);
