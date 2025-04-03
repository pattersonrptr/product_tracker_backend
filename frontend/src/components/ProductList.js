import React, { useEffect, useState } from "react";
import Pagination from "./Pagination";
import "./ProductList.css";

const ProductList = () => {
  const [products, setProducts] = useState([]);
  //  const [filters, setFilters] = useState({ title: "", min_price: "", max_price: "" });
  const [filters, setFilters] = useState({});
  const [page, setPage] = useState(1);
  const [totalProducts, setTotalProducts] = useState(0);
  const itemsPerPage = 50;

  // Fetch products with filters and pagination
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

  const handleSearch = (e) => {
    setFilters({ ...filters, title: e.target.value });
  };

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  // Fetch products when page or filters change
  useEffect(() => {
    fetchProducts();
    fetchStats();
  }, [filters, page]);

  return (
    <div className="product-list">
      <div className="filters">
        <input
          type="text"
          placeholder="Buscar produto..."
          value={filters.title}
          onChange={handleSearch}
        />
        <input
          type="number"
          placeholder="Preço mínimo"
          name="min_price"
          value={filters.min_price}
          onChange={handleFilterChange}
        />
        <input
          type="number"
          placeholder="Preço máximo"
          name="max_price"
          value={filters.max_price}
          onChange={handleFilterChange}
        />
      </div>
      <ul>
        {products.map((product) => (
          <li key={product.id}>
            <a href={product.url}>{product.title}</a> - R$ {product.price}
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
