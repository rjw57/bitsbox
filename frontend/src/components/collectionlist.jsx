import React from 'react';
import ReactList from 'react-list';
import Relay from 'react-relay';

import {GridList, GridTile} from 'material-ui/GridList';
import FloatingActionButton from 'material-ui/FloatingActionButton';
import ContentAdd from 'material-ui/svg-icons/content/add';

let Collection = Relay.createContainer(
  (props) => {
    let collection = props.collection;
    return <div>
      {collection.contentCount} &times; {collection.name}
      ({collection.description})
    </div>;
  }, {
    fragments: {
      collection: () => Relay.QL`
        fragment on Collection {
          id, name, description, contentCount
        }
      `
    }
  }
);

// id, ${Collection.getFragment('collection')}

let CollectionList = Relay.createContainer(
  (props) => {
    let listItems = props.collections.edges.map((collection) => (
      <GridTile key={collection.node.id} title={collection.node.name} />
    ));
    console.log(listItems);
    return <div>
      <GridList>{listItems}</GridList>
      <FloatingActionButton secondary={true}>
        <ContentAdd />
      </FloatingActionButton>
    </div>
  }, {
    fragments: {
      collections: () => Relay.QL`
        fragment on CollectionConnection {
          edges {
            node {
              id
              ... on Collection {
                name
              }
            }
          }
        }
      `
    }
  }
);

export default CollectionList;
