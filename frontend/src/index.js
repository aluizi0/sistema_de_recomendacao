import React from 'react';
import './index.css';
import App from './App';
import { createRoot } from 'react-dom/client';
import reportWebVitals from './reportWebVitals';

const root = document.getElementById('root');
createRoot(root).render(
    <App />
);

// Se você quiser começar a medir o desempenho no modo de produção com o Google Analytics, remova o comentário da linha abaixo
// Saiba mais em: https://bit.ly/CRA-vitals
// reportWebVitals(console.log);