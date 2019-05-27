import React, { Component } from "react";
import { HashRouter, Route, Switch } from "react-router-dom";

import "@coreui/icons/css/coreui-icons.min.css";
import "@coreui/coreui/dist/css/coreui.css";

import Full from "./containers/DefaultLayout/DefaultLayout.js";

class App extends Component {
  render() {
    return (
      <HashRouter>
        <Switch>
          <Route path="/" name="Home" component={Full} />
        </Switch>
      </HashRouter>
    );
  }
}

export default App;
