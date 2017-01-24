import React from 'react';
import Relay from 'react-relay';

import CollectionList from './collectionlist.jsx';

export const CollectionsScreen = () => (
  <Relay.RootContainer
    Component={CollectionList}
    route={{
      queries: { collections: () => Relay.QL`query { collections }` },
      name: 'CollectionsRoute',
      params: {}
    }}
  >
  </Relay.RootContainer>
);

export default CollectionsScreen;
