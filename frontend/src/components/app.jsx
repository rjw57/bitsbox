import React from 'react';
import Relay from 'react-relay';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';

import AppBar from 'material-ui/AppBar';

import CollectionList from './collectionlist.jsx';
import css from './app.less';

export default (props) => (
    <MuiThemeProvider>
      <div>
        <AppBar title="hello"/>
        <Relay.RootContainer
          Component={CollectionList}
          route={{
            queries: { collections: () => Relay.QL`query { collections }` },
            name: 'CollectionsRoute',
            params: {}
          }}
        />
      </div>
    </MuiThemeProvider>
);
