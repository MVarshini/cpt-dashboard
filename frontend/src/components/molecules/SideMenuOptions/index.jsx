import * as CONSTANTS from "@/assets/constants/SidemenuConstants";

import { Nav, NavItem, NavList } from "@patternfly/react-core";
import { navigateWithParams, setActiveItem } from "@/actions/sideMenuActions";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { useEffect } from "react";

const sideMenuOptions = [
  {
    id: CONSTANTS.HOME_NAV,
    key: "home",
    displayName: "Home",
    type: "cpt",
  },
  {
    id: CONSTANTS.OCP_NAV,
    key: "ocp",
    displayName: "OCP",
    type: "ocp",
  },
  {
    id: CONSTANTS.QUAY_NAV,
    key: "quay",
    displayName: "Quay",
    type: "quay",
  },
  {
    id: CONSTANTS.TELCO_NAV,
    key: "telco",
    displayName: "Telco",
    type: "telco",
  },
];

const MenuOptions = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const activeMenuItem = useSelector((state) => state.sidemenu.activeMenuItem);

  const onSelect = (_event, item) => {
    dispatch(setActiveItem(item.itemId));
  };

  useEffect(() => {
    if (pathname !== "/") {
      const currPath = pathname.replace(/^.*[/]([^/]+)[/]*$/, "$1");

      dispatch(setActiveItem(currPath));
    }
  }, [dispatch, pathname]);

  return (
    <>
      <Nav onSelect={onSelect}>
        <NavList>
          {sideMenuOptions.map((option) => {
            return (
              <NavItem
                key={option.key}
                itemId={option.id}
                isActive={activeMenuItem === option.id}
                onClick={() =>
                  dispatch(
                    navigateWithParams(option.key, option.type, navigate)
                  )
                }
              >
                {option.displayName}
              </NavItem>
            );
          })}
        </NavList>
      </Nav>
    </>
  );
};

export default MenuOptions;
