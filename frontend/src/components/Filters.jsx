import React from "react";

const Filters = ({ filters, onSearchChange, onFilterChange }) => {
  const handleNumberInputChange = (e) => {
    const { name, value } = e.target;
    const sanitizedValue = value === "" || parseFloat(value) >= 0 ? value : 0;
    onFilterChange({ target: { name, value: sanitizedValue } });
  };

  return (
    <div className="filters">
      <div className="filter-group">
        <label htmlFor="search-product">Search Product</label>
        <input
          id="search-product"
          type="text"
          placeholder="Ex: Smartphone"
          value={filters.title || ""}
          onChange={onSearchChange}
        />
      </div>

      <div className="filter-group">
        <label htmlFor="min-price">Minimum Price</label>
        <input
          id="min-price"
          type="number"
          placeholder="0"
          name="min_price"
          value={filters.min_price || ""}
          onChange={handleNumberInputChange}
        />
      </div>

      <div className="filter-group">
        <label htmlFor="max-price">Maximum Price</label>
        <input
          id="max-price"
          type="number"
          placeholder="1000"
          name="max_price"
          value={filters.max_price || ""}
          onChange={handleNumberInputChange}
        />
      </div>

      <div className="filter-group">
        <label htmlFor="created-after">Created After</label>
        <input
          id="created-after"
          type="date"
          name="created_after"
          value={filters.created_after || ""}
          onChange={onFilterChange}
        />
      </div>

      <div className="filter-group">
        <label htmlFor="created-before">Created Before</label>
        <input
          id="created-before"
          type="date"
          name="created_before"
          value={filters.updated_after || ""}
          onChange={onFilterChange}
        />
      </div>

      <div className="filter-group">
        <label htmlFor="updated-after">Updated After</label>
        <input
          id="updated-after"
          type="date"
          name="updated_after"
          value={filters.updated_after || ""}
          onChange={onFilterChange}
        />
      </div>

      <div className="filter-group">
        <label htmlFor="updated-before">Updated Before</label>
        <input
          id="updated-before"
          type="date"
          name="updated_before"
          value={filters.updated_before || ""}
          onChange={onFilterChange}
        />
      </div>

      {/* <div className="filter-group">
        <label htmlFor="url-filter">Product URL</label>
        <input
          id="url-filter"
          type="text"
          placeholder="https://example.com/product"
          name="url"
          value={filters.url}
          onChange={onFilterChange}
        />
      </div> */}
    </div>
  );
};

export default Filters;
