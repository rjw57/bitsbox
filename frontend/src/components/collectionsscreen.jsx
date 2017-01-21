import React from 'react';
import Relay from 'react-relay';
import AppBar from 'material-ui/AppBar';

import CollectionList from './collectionlist.jsx';

export const CollectionsScreen = () => (
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
);

export default CollectionsScreen;
