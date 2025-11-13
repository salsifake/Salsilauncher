import React, { useState, useEffect } from 'react';
import axios from 'axios';
import GameCard from '../components/GameCard';

function Biblioteca() {
  const [jogos, setJogos] = useState([]);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/jogos')
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