import React from 'react';
import Relay from 'react-relay';
import { render } from 'react-dom';
import injectTapEventPlugin from 'react-tap-event-plugin';

import App from './components/app.jsx';

injectTapEventPlugin();

if(typeof(GRAPHQL_ENDPOINT) === 'undefined') {
  throw new Error('No graphQL endpoint defined');
}

console.log('Using graphql endpoint: ' + GRAPHQL_ENDPOINT);
Relay.injectNetworkLayer(new Relay.DefaultNetworkLayer(GRAPHQL_ENDPOINT));

render(<App/>, document.getElementById('app'));
