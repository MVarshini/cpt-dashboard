const getCloneDeep = async () => (await import("lodash/cloneDeep")).default;

export const deleteAppliedFilters =
  (filterKey, filterValue, currState) => async (dispatch, getState) => {
    const cloneDeep = await getCloneDeep();
    const appliedFilters = cloneDeep(getState()[currState].appliedFilters);

    const index = appliedFilters[filterKey]
      ?.toString()
      ?.toLowerCase()
      .indexOf(filterValue?.toString()?.toLowerCase());
    if (index >= 0) {
      appliedFilters[filterKey].splice(index, 1);
      if (appliedFilters[filterKey].length === 0) {
        delete appliedFilters[filterKey];
      }
    }
    return appliedFilters;
  };

export const getSelectedFilter =
  (selectedCategory, selectedOption, currState, isFromMetrics) =>
  async (dispatch, getState) => {
    const cloneDeep = await getCloneDeep();
    const selectedFilters = cloneDeep(getState()[currState].selectedFilters);

    const obj = selectedFilters.find((i) => i.name === selectedCategory);

    const objValue = obj.value;
    if (objValue.includes(selectedOption)) {
      const arr = objValue.filter((selection) => selection !== selectedOption);
      obj.value = arr;
    } else {
      obj.value = isFromMetrics
        ? [selectedOption]
        : [...obj.value, selectedOption];
    }

    return selectedFilters;
  };

const convertObjectToQS = (filter) => {
  const queryString = Object.entries(filter)
    .map(([key, values]) => `${key}='${values.join("','")}'`)
    .join("&");

  return queryString;
};
export const getRequestParams = (type) => (dispatch, getState) => {
  const { start_date, end_date, perPage, offset, sort, appliedFilters } =
    getState()[type];

  let filter = "";
  if (Object.keys(appliedFilters).length > 0) {
    filter = convertObjectToQS(appliedFilters);
  }
  console.log(offset);
  const params = {
    pretty: true,
    ...(start_date && { start_date }),
    ...(end_date && { end_date }),
    size: perPage,
    offset: offset,
    ...(sort && { sort }),
    ...(filter && { filter }),
  };

  return params;
};
