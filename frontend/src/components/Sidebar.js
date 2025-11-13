// frontend/src/components/Sidebar.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './Sidebar.css';
import AccordionItem from './AccordionItem'

function Sidebar() {
  const [colecoes, setColecoes] = useState([]);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/colecoes')
      .then(response => {
        setColecoes(response.data);
      })
      .catch(error => console.error('Erro ao buscar coleções:', error));
  }, []);

  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        <h2 className="sidebar-title">Biblioteca</h2>
        <Link to="/" className="nav-link">Home</Link>
        <Link to="/colecoes" className="nav-link">Coleções</Link>
        <Link to="/buscar" className="nav-link">Buscar</Link>
        <Link to="/adicionar-jogo" className="nav-link">Adicionar Jogo</Link>
      </nav>

      <div className="sidebar-divider"></div>

      <div className="colecoes-list">
        <h3 className="sidebar-subtitle">Minhas Coleções</h3>
        {colecoes.map(colecao => (
          <AccordionItem key={colecao.id} colecao={colecao} />
        ))}
      </div>
    </aside>
  );
}

export default Sidebar;