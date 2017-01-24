import React from 'react';
import { Router, Route, hashHistory, IndexRoute } from 'react-router'

import Page from './page.jsx';
import CollectionsScreen from './collectionsscreen.jsx';

export default (props) => (
  <Router history={hashHistory}>
    <Route path='/' component={Page}>
      <IndexRoute component={CollectionsScreen} />
    </Route>
  </Router>
);
