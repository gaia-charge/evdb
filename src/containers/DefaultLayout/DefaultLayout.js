import React, { Component } from "react";
import {
  Container,
  Nav,
  NavItem,
  NavLink,
  Badge,
  DropdownToggle,
  DropdownMenu
} from "reactstrap";
import {
  AppAside,
  AppAsideToggler,
  AppBreadcrumb2 as AppBreadcrumb,
  AppFooter,
  AppHeader,
  AppHeaderDropdown,
  AppNavbarBrand,
  AppSidebar,
  AppSidebarFooter,
  AppSidebarForm,
  AppSidebarHeader,
  AppSidebarMinimizer,
  // AppSidebarNav as AppSidebarNav,
  AppSidebarNav2 as AppSidebarNav,
  AppSidebarToggler
} from "@coreui/react";

class DefaultLayout extends Component {
  render() {
    return (
      <div className="app">
        <AppHeader fixed>
          <Nav className="ml-medium" navbar>
            <NavItem>
              <NavLink href="connectors">Connectors</NavLink>
            </NavItem>
          </Nav>
        </AppHeader>
      </div>
    );
  }
}

export default DefaultLayout;
