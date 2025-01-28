import React, { useState, useEffect } from 'react';
import { getAds } from '../services/api';

const AdList = () => {
  const [ads, setAds] = useState([]);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);

  useEffect(() => {
    getAds(search, page)
      .then(response => setAds(response.data))
      .catch(error => console.error(error));
  }, [search, page]);

  return (
    <div>
      <input
        type="text"
        placeholder="Pesquisar..."
        onChange={(e) => setSearch(e.target.value)}
      />
      <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
        {ads.map(ad => (
          <div key={ad.id}>
            <h3>{ad.title}</h3>
            <p>Preço: R$ {ad.price}</p>
          </div>
        ))}
      </div>
      <button onClick={() => setPage(page - 1)} disabled={page === 1}>
        Anterior
      </button>
      <button onClick={() => setPage(page + 1)}>Próxima</button>
    </div>
  );
};

export default AdList;
