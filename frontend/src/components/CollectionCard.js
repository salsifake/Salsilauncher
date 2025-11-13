// frontend/src/components/CollectionCard.js
import React from 'react';
import './CollectionCard.css'; // Vamos criar este arquivo

function CollectionCard({ colecao, onClick }) {
  // O card especial de "Criar" não tem uma coleção, então tratamos isso
  if (!colecao) {
    return (
      <div className="collection-card create-card" onClick={onClick}>
        <div className="create-card-plus">+</div>
        <div className="create-card-text">Criar Coleção</div>
      </div>
    );
  }

  return (
    <div className="collection-card" onClick={onClick}>
      {/* Lógica para a capa da coleção virá aqui */}
      <div className="collection-card-placeholder"></div>
      <div className="collection-card-name">{colecao.nome}</div>
    </div>
  );
}

export default CollectionCard;