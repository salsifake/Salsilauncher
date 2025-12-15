import React, { useState, useEffect } from 'react';
import api from '../services/api';
import GameCard from '../components/GameCard';

function Biblioteca() {
  const [jogos, setJogos] = useState([]);

  useEffect(() => {
    api.get('/jogos')
      .then(response => setJogos(response.data))
      .catch(error => console.error('Erro ao buscar jogos:', error));
  }, []);

  return (
    <main className="biblioteca-container">
      <div className="lista-jogos">
        {jogos.map(jogo => (
          <GameCard key={jogo.id} jogo={jogo} />
        ))}
      </div>
    </main>
  );
}
export default Biblioteca;