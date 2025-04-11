import React, { useEffect, useState, useCallback } from "react";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Pagination from "./Pagination";
import Filters from "./Filters";
import "./ProductList.css";

const ProductList = () => {
  const [products, setProducts] = useState([]);
  const [filters, setFilters] = useState({});
  const [page, setPage] = useState(1);
  const [totalProducts, setTotalProducts] = useState(0);
  const itemsPerPage = 50;

  const fetchProducts = useCallback(async () => {
    try {
      const validFilters = Object.fromEntries(
        Object.entries(filters).filter(
          ([_, value]) => value !== undefined && value !== ""
        )
      );

      const params = new URLSearchParams({
        ...validFilters,
        limit: itemsPerPage,
        offset: (page - 1) * itemsPerPage,
      });

      const response = await fetch(`http://localhost:8000/products/?${params}`);
      if (response.ok) {
        const data = await response.json();
        setProducts(data.data || []);
      } else {
        console.error("Failed to fetch products");
        setProducts([]);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
      setProducts([]);
    }
  }, [filters, page, itemsPerPage]);

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
        toast.success("Product deleted successfully!");
      } else {
        toast.error("Failed to delete product");
      }
    } catch (error) {
      toast.error("Error deleting product");
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

  const formatDate = (dateString) => {
    return new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short",
      timeStyle: "short",
    }).format(new Date(dateString));
  };

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  useEffect(() => {
    fetchStats();
  }, [filters, page]);

  return (
    <div className="product-list">
      <Filters
        filters={filters}
        onSearchChange={handleSearch}
        onFilterChange={handleFilterChange}
      />

      <table className="product-table">
        <thead>
          <tr>
            <th>Product ID</th>
            <th>Title</th>
            <th>Price</th>
            <th>Created At</th>
            <th>Updated At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {Array.isArray(products) ? (
            products.map((product) => (
              <tr key={product.id}>
                <td>#{product.id}</td>
                <td>
                  <a
                    href={product.url || "#"}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {product.title || "No Title"}
                  </a>
                </td>
                <td>{product.price || "N/A"}</td>
                <td>
                  {product.created_at ? formatDate(product.created_at) : "N/A"}
                </td>
                <td>
                  {product.updated_at ? formatDate(product.updated_at) : "N/A"}
                </td>
                <td>
                  <button className="update-button">Update</button>
                  <button
                    className="delete-button"
                    onClick={() => confirmDelete(product.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="6">No products available</td>
            </tr>
          )}
        </tbody>
      </table>

      <Pagination
        currentPage={page}
        totalItems={totalProducts}
        itemsPerPage={itemsPerPage}
        onPageChange={(newPage) => setPage(newPage)}
      />

      <ToastContainer position="bottom-right" autoClose={3000} />
    </div>
  );
};

export default ProductList;
