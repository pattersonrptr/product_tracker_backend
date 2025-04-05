import React from "react";
import ProductList from "./components/ProductList";
import "./App.css";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Price Monitoring</h1>
      </header>
      <div className="App-body">
        <aside className="App-sidebar">{/* Sidebar empty for now */}</aside>
        <main className="App-main">
          <ProductList />
        </main>
      </div>
      <footer className="App-footer">
        &copy; {new Date().getFullYear()} Sistema de Produtos
      </footer>
    </div>
  );
}

export default App;
