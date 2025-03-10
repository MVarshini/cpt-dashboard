import {
  applyCPTDateFilter,
  removeCPTAppliedFilters,
  setCPTAppliedFilters,
  setCPTCatFilters,
  setCPTOtherSummaryFilter,
} from "./homeActions";
import {
  applyOCPDateFilter,
  removeOCPAppliedFilters,
  setOCPAppliedFilters,
  setOCPCatFilters,
  setOCPOtherSummaryFilter,
} from "./ocpActions";
import {
  applyQuayDateFilter,
  removeQuayAppliedFilters,
  setQuayAppliedFilters,
  setQuayCatFilters,
  setQuayOtherSummaryFilter,
} from "./quayActions";
import {
  applyTelcoDateFilter,
  removeTelcoAppliedFilters,
  setTelcoAppliedFilters,
  setTelcoCatFilters,
  setTelcoOtherSummaryFilter,
} from "./telcoActions";

import store from "@/store/store";

const { dispatch } = store;

const filterActions = {
  cpt: {
    setCategory: setCPTCatFilters,
    setApplied: setCPTAppliedFilters,
    removeApplied: removeCPTAppliedFilters,
    setDate: applyCPTDateFilter,
    setOtherSummary: setCPTOtherSummaryFilter,
  },
  ocp: {
    setCategory: setOCPCatFilters,
    setApplied: setOCPAppliedFilters,
    removeApplied: removeOCPAppliedFilters,
    setDate: applyOCPDateFilter,
    setOtherSummary: setOCPOtherSummaryFilter,
  },
  quay: {
    setCategory: setQuayCatFilters,
    setApplied: setQuayAppliedFilters,
    removeApplied: removeQuayAppliedFilters,
    setDate: applyQuayDateFilter,
    setOtherSummary: setQuayOtherSummaryFilter,
  },
  telco: {
    setCategory: setTelcoCatFilters,
    setApplied: setTelcoAppliedFilters,
    removeApplied: removeTelcoAppliedFilters,
    setDate: applyTelcoDateFilter,
    setOtherSummary: setTelcoOtherSummaryFilter,
  },
};

export const setCatFilters = (category, currType) => {
  filterActions[currType]?.setCategory &&
    dispatch(filterActions[currType].setCategory(category));
};

export const setAppliedFilters = (navigation, currType) => {
  filterActions[currType]?.setApplied &&
    dispatch(filterActions[currType].setApplied(navigation));
};

export const removeAppliedFilters = (key, value, navigation, currType) => {
  filterActions[currType]?.setApplied &&
    dispatch(filterActions[currType].removeApplied(key, value, navigation));
};

export const setDateFilter = (date, key, navigation, currType) => {
  filterActions[currType]?.setApplied &&
    dispatch(filterActions[currType].setDate(date, key, navigation));
};

export const setOtherSummaryFilter = (currType) => {
  filterActions[currType]?.setApplied &&
    dispatch(filterActions[currType].setOtherSummary());
};
