import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/products/')
      .then((response) => response.json())
      .then((data) => setProducts(data))
      .catch((error) => console.error('Error when fetching products:', error));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Lista de Produtos</h1>
        <ul>
          {products.map((product) => (
            <li key={product.id}>
              # {product.id} - <a href={product.url}>{product.title}</a> - R$ {product.price}
            </li>
          ))}
        </ul>
      </header>
    </div>
  );
}

export default App;
