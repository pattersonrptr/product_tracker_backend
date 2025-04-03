import React, { useEffect, useState } from "react";
import Pagination from "./Pagination";
import "./ProductList.css";

const ProductList = () => {
  const [products, setProducts] = useState([]);
  const [filters, setFilters] = useState({
    //    title: "",
    //    min_price: "",
    //    max_price: "",
    //    created_after: "",
    //    created_before: "",
    //    updated_after: "",
    //    updated_before: "",
    //    url: ""
  });
  const [page, setPage] = useState(1);
  const [totalProducts, setTotalProducts] = useState(0);
  const [notification, setNotification] = useState("");
  const itemsPerPage = 50;

  const fetchProducts = async () => {
    try {
      const params = new URLSearchParams({
        ...filters,
        limit: itemsPerPage,
        offset: (page - 1) * itemsPerPage,
      });

      const response = await fetch(`http://localhost:8000/products/?${params}`);
      if (response.ok) {
        const data = await response.json();
        setProducts(data);
      } else {
        console.error("Failed to fetch products");
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch("http://localhost:8000/products/stats/");
      if (response.ok) {
        const data = await response.json();
        setTotalProducts(data.total_products);
      } else {
        console.error("Failed to fetch stats");
      }
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  const deleteProduct = async (productId) => {
    try {
      const response = await fetch(
        `http://localhost:8000/products/${productId}/`,
        {
          method: "DELETE",
        }
      );
      if (response.ok) {
        setProducts(products.filter((product) => product.id !== productId));
        setTotalProducts((prevTotal) => prevTotal - 1);
        setNotification("Product deleted successfully!");
        setTimeout(() => setNotification(""), 3000);
      } else {
        console.error("Failed to delete product");
      }
    } catch (error) {
      console.error("Error deleting product:", error);
    }
  };

  const handleSearch = (e) => {
    setFilters({ ...filters, title: e.target.value });
  };

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const confirmDelete = (productId) => {
    if (window.confirm("Are you sure you want to delete this product?")) {
      deleteProduct(productId);
    }
  };

  useEffect(() => {
    fetchProducts();
    fetchStats();
  }, [filters, page]);

  return (
    <div className="product-list">
      <div className="filters">
        <div className="filter-group">
          <label htmlFor="search-product">Search Product</label>
          <input
            id="search-product"
            type="text"
            placeholder="Ex: Smartphone"
            value={filters.title}
            onChange={handleSearch}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="min-price">Minimum Price</label>
          <input
            id="min-price"
            type="number"
            placeholder="0"
            name="min_price"
            value={filters.min_price}
            onChange={handleFilterChange}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="max-price">Maximum Price</label>
          <input
            id="max-price"
            type="number"
            placeholder="1000"
            name="max_price"
            value={filters.max_price}
            onChange={handleFilterChange}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="created-after">Created After</label>
          <input
            id="created-after"
            type="date"
            name="created_after"
            value={filters.created_after}
            onChange={handleFilterChange}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="created-before">Created Before</label>
          <input
            id="created-before"
            type="date"
            name="created_before"
            value={filters.created_before}
            onChange={handleFilterChange}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="updated-after">Updated After</label>
          <input
            id="updated-after"
            type="date"
            name="updated_after"
            value={filters.updated_after}
            onChange={handleFilterChange}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="updated-before">Updated Before</label>
          <input
            id="updated-before"
            type="date"
            name="updated_before"
            value={filters.updated_before}
            onChange={handleFilterChange}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="url-filter">Product URL</label>
          <input
            id="url-filter"
            type="text"
            placeholder="https://example.com/product"
            name="url"
            value={filters.url}
            onChange={handleFilterChange}
          />
        </div>
      </div>

      {notification && <div className="notification">{notification}</div>}

      <ul>
        {products.map((product) => (
          <li key={product.id}>
            <span>#{product.id}&emsp;</span>
            <a href={product.url}>{product.title}</a> - R$ {product.price}
            <button
              className="delete-button"
              onClick={() => confirmDelete(product.id)}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>

      <Pagination
        currentPage={page}
        totalItems={totalProducts}
        itemsPerPage={itemsPerPage}
        onPageChange={(newPage) => setPage(newPage)}
      />
    </div>
  );
};

export default ProductList;
