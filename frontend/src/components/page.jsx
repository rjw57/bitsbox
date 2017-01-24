// <Page> wraps the default navigation and layout for the app.

import React from 'react';
import Relay from 'react-relay';

import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import AppBar from 'material-ui/AppBar';

import css from './page.less';

export const Page = (props) => (
  <MuiThemeProvider>
    <div id="pageBody">
      <AppBar title={ props.title ? props.title : 'Title' } />
      <div id="pageContent">{ props.children }</div>
    </div>
  </MuiThemeProvider>
)

export default Page;

