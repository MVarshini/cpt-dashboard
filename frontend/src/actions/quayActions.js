import * as API_ROUTES from "@/utils/apiConstants";
import * as TYPES from "@/actions/types.js";

import { appendDateFilter, appendQueryString } from "@/utils/helper.js";
import {
  deleteAppliedFilters,
  getRequestParams,
  getSelectedFilter,
} from "./commonActions";

import API from "@/utils/axiosInstance";
import { START_PAGE } from "@/assets/constants/paginationConstants";
import { cloneDeep } from "lodash";
import { showFailureToast } from "@/actions/toastActions";

export const fetchQuayJobsData =
  (shouldStartFresh = false) =>
  async (dispatch, getState) => {
    try {
      dispatch({ type: TYPES.LOADING });

      const { results } = cloneDeep(getState().quay);
      const params = dispatch(getRequestParams("quay"));

      const response = await API.get(API_ROUTES.QUAY_JOBS_API_V1, {
        params,
      });
      if (response.status === 200) {
        const startDate = response.data.startDate,
          endDate = response.data.endDate;
        //on initial load startDate and endDate are empty, so from response append to url
        appendDateFilter(startDate, endDate);
        dispatch({
          type: TYPES.SET_QUAY_DATE_FILTER,
          payload: {
            start_date: startDate,
            end_date: endDate,
          },
        });
      }
      if (response?.data?.results?.length > 0) {
        if (shouldStartFresh) {
          dispatch(setQuayPage(1));
        }
        dispatch({
          type: TYPES.SET_QUAY_JOBS_DATA,
          payload: shouldStartFresh
            ? response.data.results
            : [...results, ...response.data.results],
        });
        dispatch(tableReCalcValues());
      }
    } catch (error) {
      dispatch(showFailureToast());
    }
    dispatch({ type: TYPES.COMPLETED });
  };

export const setQuayPage = (pageNo) => ({
  type: TYPES.SET_QUAY_PAGE,
  payload: pageNo,
});
export const setQuayOffset = (offset) => ({
  type: TYPES.SET_QUAY_OFFSET,
  payload: offset,
});

export const setQuayPageOptions = (page, perPage) => ({
  type: TYPES.SET_QUAY_PAGE_OPTIONS,
  payload: { page, perPage },
});
export const setQuaySortIndex = (index) => ({
  type: TYPES.SET_QUAY_SORT_INDEX,
  payload: index,
});
export const setQuaySortDir = (direction) => ({
  type: TYPES.SET_QUAY_SORT_DIR,
  payload: direction,
});
export const sliceQuayTableRows =
  (startIdx, endIdx) => (dispatch, getState) => {
    const results = [...getState().quay.results];

    dispatch({
      type: TYPES.SET_QUAY_INIT_JOBS,
      payload: results.slice(startIdx, endIdx),
    });
  };

export const setQuayCatFilters = (category) => (dispatch, getState) => {
  const filterData = [...getState().quay.filterData];
  const options = filterData.filter((item) => item.name === category)[0].value;
  const list = options.map((item) => ({ name: item, value: item }));

  dispatch({
    type: TYPES.SET_QUAY_CATEGORY_FILTER,
    payload: category,
  });
  dispatch({
    type: TYPES.SET_QUAY_FILTER_OPTIONS,
    payload: list,
  });
};
export const removeQuayAppliedFilters =
  (filterKey, filterValue, navigate) => (dispatch, getState) => {
    const { start_date, end_date } = getState().quay;

    const appliedFilters = dispatch(
      deleteAppliedFilters(filterKey, filterValue, "quay")
    );

    dispatch({
      type: TYPES.SET_QUAY_APPLIED_FILTERS,
      payload: appliedFilters,
    });
    appendQueryString({ ...appliedFilters, start_date, end_date }, navigate);
    dispatch(applyFilters());
  };

export const applyFilters = () => (dispatch) => {
  dispatch(setQuayPage(START_PAGE));

  dispatch(fetchQuayJobsData(true));
  dispatch(tableReCalcValues());
  dispatch(buildFilterData());
};
export const setQuayAppliedFilters = (navigate) => (dispatch, getState) => {
  const { selectedFilters, start_date, end_date } = getState().quay;

  const appliedFilterArr = selectedFilters.filter((i) => i.value.length > 0);

  const appliedFilters = {};
  appliedFilterArr.forEach((item) => {
    appliedFilters[item["name"]] = item.value;
  });

  dispatch({
    type: TYPES.SET_QUAY_APPLIED_FILTERS,
    payload: appliedFilters,
  });
  appendQueryString({ ...appliedFilters, start_date, end_date }, navigate);
  dispatch(applyFilters());
};

export const setSelectedFilterFromUrl = (params) => (dispatch, getState) => {
  const selectedFilters = cloneDeep(getState().quay.selectedFilters);
  for (const key in params) {
    selectedFilters.find((i) => i.name === key).value = params[key].split(",");
  }
  dispatch({
    type: TYPES.SET_QUAY_SELECTED_FILTERS,
    payload: selectedFilters,
  });
};

export const setFilterFromURL = (searchParams) => ({
  type: TYPES.SET_QUAY_APPLIED_FILTERS,
  payload: searchParams,
});

export const setSelectedFilter =
  (selectedCategory, selectedOption, isFromMetrics) => (dispatch) => {
    const selectedFilters = dispatch(
      getSelectedFilter(selectedCategory, selectedOption, "quay", isFromMetrics)
    );
    dispatch({
      type: TYPES.SET_QUAY_SELECTED_FILTERS,
      payload: selectedFilters,
    });
  };
export const setQuayDateFilter =
  (start_date, end_date, navigate) => (dispatch, getState) => {
    const appliedFilters = getState().quay.appliedFilters;

    dispatch({
      type: TYPES.SET_QUAY_DATE_FILTER,
      payload: {
        start_date,
        end_date,
      },
    });

    appendQueryString({ ...appliedFilters, start_date, end_date }, navigate);

    dispatch(fetchQuayJobsData());
  };

export const setQuayOtherSummaryFilter = () => (dispatch, getState) => {
  const filteredResults = [...getState().quay.results];
  const keyWordArr = ["success", "failure"];
  const data = filteredResults.filter(
    (item) => !keyWordArr.includes(item.jobStatus?.toLowerCase())
  );
  dispatch({
    type: TYPES.SET_QUAY_FILTERED_DATA,
    payload: data,
  });
  dispatch(tableReCalcValues());
};

export const getQuaySummary = (summary) => (dispatch) => {
  const countObj = {
    successCount: summary["success"] ?? 0,
    failureCount: summary["failure"] ?? 0,
    othersCount: 0,
    total: summary["total"] ?? 0,
  };
  for (const key in summary) {
    if (key !== "total" && key !== "success" && key !== "failure") {
      countObj["othersCount"] += summary[key];
    }
  }
  dispatch({
    type: TYPES.SET_QUAY_SUMMARY,
    payload: countObj,
  });
};

export const setTableColumns = (key, isAdding) => (dispatch, getState) => {
  let tableColumns = [...getState().quay.tableColumns];
  const tableFilters = getState().quay.tableFilters;

  if (isAdding) {
    const filterObj = tableFilters.find((item) => item.value === key);
    tableColumns.push(filterObj);
  } else {
    tableColumns = tableColumns.filter((item) => item.value !== key);
  }

  dispatch({
    type: TYPES.SET_QUAY_COLUMNS,
    payload: tableColumns,
  });
};

export const fetchGraphData = (uuid) => async (dispatch, getState) => {
  try {
    dispatch({ type: TYPES.GRAPH_LOADING });

    const graphData = getState().quay.graphData;
    const hasData = graphData.filter((a) => a.uuid === uuid).length > 0;
    if (!hasData) {
      const response = await API.get(`${API_ROUTES.QUAY_GRAPH_API_V1}/${uuid}`);

      if (response.status === 200) {
        const result = Object.keys(response.data).map((key) => [
          key,
          response.data[key],
        ]);
        dispatch({
          type: TYPES.SET_QUAY_GRAPH_DATA,
          payload: { uuid, data: result },
        });
      }
    }
  } catch (error) {
    dispatch(showFailureToast());
  }
  dispatch({ type: TYPES.GRAPH_COMPLETED });
};

export const tableReCalcValues = () => (dispatch, getState) => {
  const { page, perPage } = getState().quay;
  const startIdx = page !== 1 ? (page - 1) * perPage : 0;
  const endIdx = page !== 1 ? page * perPage - 1 : perPage;

  dispatch(sliceQuayTableRows(startIdx, endIdx));
};

export const buildFilterData = () => async (dispatch, getState) => {
  try {
    const { tableFilters, categoryFilterValue } = getState().quay;

    const params = dispatch(getRequestParams("quay"));

    const response = await API.get("/api/v1/quay/filters", { params });

    if (response.status === 200 && response?.data?.filterData?.length > 0) {
      let data = cloneDeep(response.data.filterData);
      console.log(data);

      dispatch(getQuaySummary(response.data.summary));

      const activeFilter = categoryFilterValue || tableFilters[0].name;
      await dispatch(setQuayCatFilters(activeFilter));
    }
  } catch (error) {
    console.log(error);
  }
};
