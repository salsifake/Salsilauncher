import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Biblioteca from './pages/Biblioteca';
import DetalhesJogo from './pages/DetalhesJogo';
import Sidebar from './components/Sidebar'; // Importamos a Sidebar
import BuscaPage from './pages/BuscaPage'
import AdicionarJogoPage from './pages/AdicionarJogoPage';

// Criamos uma página placeholder para o gerenciador de coleções
function ColecoesPage() { return <h1 style={{padding: '2rem'}}>Gerenciar Coleções</h1>; }

function App() {
  return (
    <Router>
      <div className="app-layout">
        <Sidebar /> {/* A Sidebar agora é fixa */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Biblioteca />} />
            <Route path="/colecoes" element={<ColecoesPage />} />
            <Route path="/jogo/:id" element={<DetalhesJogo />} />
            <Route path="/buscar" element={<BuscaPage />} />
            <Route path="/adicionar-jogo" element={<AdicionarJogoPage />} />
            <Route path="/jogo/:id/editar" element={<AdicionarJogoPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;