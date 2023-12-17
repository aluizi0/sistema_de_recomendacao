import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);

// Se você quiser começar a medir o desempenho no modo de produção com o Google Analytics, remova o comentário da linha abaixo
// Saiba mais em: https://bit.ly/CRA-vitals
// reportWebVitals(console.log);