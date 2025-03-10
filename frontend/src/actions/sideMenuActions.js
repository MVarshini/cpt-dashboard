import * as TYPES from "./types";

export const setActiveItem = (item) => {
  return {
    type: TYPES.SET_ACTIVE_MENU_ITEM,
    payload: item,
  };
};

export const toggleSideMenu = (isOpen) => ({
  type: TYPES.TOGGLE_SIDE_MENU,
  payload: isOpen,
});

export const navigateWithParams =
  (key, type, navigate) => (dispatch, getState) => {
    const { appliedFilters, start_date, end_date } = getState()[type];
    let params = {};
    if (start_date) {
      params.start_date = start_date;
    }
    if (end_date) {
      params.end_date = end_date;
    }
    if (Object.keys(appliedFilters).length > 0) {
      params = { ...params, ...appliedFilters };
    }
    if (Object.keys(params).length > 0) {
      const queryString = new URLSearchParams(params).toString();
      navigate({
        pathname: `/${key}`,
        search: `?${queryString}`,
      });
    } else {
      navigate(key);
    }
  };
