import React from 'react';
import ReactList from 'react-list';
import Relay from 'react-relay';

import TextField from 'material-ui/TextField';
import {List, ListItem} from 'material-ui/List';
import FloatingActionButton from 'material-ui/FloatingActionButton';
import ContentAdd from 'material-ui/svg-icons/content/add';
import muiThemeable from 'material-ui/styles/muiThemeable';

const fabStyle = {
  position: 'fixed', right: 16, bottom: 16
}

const CollectionList = Relay.createContainer(
  muiThemeable()((props) => {
    let listItems = props.collections.edges.map((edge) => {
      let collection = edge.node;

      let locationDesc = null;
      if(collection.drawer) {
        locationDesc = collection.drawer.label + ' in ' +
          collection.drawer.cabinet.name;
      }

      let desc = collection.name;
      if(collection.description) {
        desc += ', ' + collection.description;
      }

      return <ListItem
        key={collection.id}
        primaryText={desc}
        secondaryText={locationDesc}>
      </ListItem>
    });
    return <div>
      <TextField hintText='Search…' />
      <List>{listItems}</List>
      <FloatingActionButton secondary={true} style={fabStyle}>
        <ContentAdd />
      </FloatingActionButton>
    </div>
  }), {
    fragments: {
      collections: () => Relay.QL`
        fragment on CollectionConnection {
          edges {
            node {
              id
              ... on Collection {
                name
                description
                drawer {
                  label
                  cabinet {
                    name
                  }
                }
              }
            }
          }
        }
      `
    }
  }
);

export default CollectionList;
