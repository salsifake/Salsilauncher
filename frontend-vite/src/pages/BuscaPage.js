// frontend/src/pages/BuscaPage.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './BuscaPage.css';
import api from '../services/api';

function BuscaPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [tags, setTags] = useState([]);
  const [activeFilters, setActiveFilters] = useState(new Set());
  const [results, setResults] = useState([]);

  useEffect(() => {
    api.get('/tags').then(res => setTags(res.data));
  }, []);

  const handleSearch = () => {
    const params = new URLSearchParams();
    params.append('q', searchTerm);
    if (activeFilters.size > 0) {
      params.append('tags', Array.from(activeFilters).join(','));
    }
    api.get(`/jogos?${params.toString()}`).then(res => setResults(res.data));
  };

  const handleRandom = () => {
    const params = new URLSearchParams();
    if (activeFilters.size > 0) {
      params.append('tags', Array.from(activeFilters).join(','));
    }
    api.get(`/jogos/aleatorio?${params.toString()}`).then(res => setResults(res.data));
  };

  const toggleFilter = (tag) => {
    setActiveFilters(prev => {
      const newFilters = new Set(prev);
      if (newFilters.has(tag)) {
        newFilters.delete(tag);
      } else {
        newFilters.add(tag);
      }
      return newFilters;
    });
  };

  return (
    <div className="busca-page-layout">
      <div className="busca-main">
        <h1>Buscar Jogos</h1>
        <div className="search-bar">
          <input type="text" value={searchTerm} onChange={e => setSearchTerm(e.target.value)} placeholder="Buscar por nome, studio, descrição..." />
          <button onClick={handleSearch}>Buscar</button>
          <button onClick={handleRandom}>Aleatório</button>
        </div>
        <div className="search-results">
          {results.map(jogo => (
            <Link to={`/jogo/${jogo.id}`} key={jogo.id} className="search-result-item">
              <img src={jogo.imagem_capa ? `/${jogo.imagem_capa}` : 'placeholder.png'} alt={jogo.nome} />
              <div className="result-info">
                <h3>{jogo.nome}</h3>
                <p>{jogo.studio || 'N/A'}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
      <div className="busca-sidebar">
        <h3>Filtros</h3>
        {tags.map(tag => (
          <div key={tag} className="filter-item">
            <input type="checkbox" id={tag} checked={activeFilters.has(tag)} onChange={() => toggleFilter(tag)} />
            <label htmlFor={tag}>{tag}</label>
          </div>
        ))}
      </div>
    </div>
  );
}
export default BuscaPage;