import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';

function TreePage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/Regras/Arvore/display');
        const treeData = await response.json();
        setData(treeData);
      } catch (error) {
        console.error('Failed to fetch tree data:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      {data && <div>{JSON.stringify(data)}</div>}
    </div>
  );
}

function HomePage() {
  const [question, setQuestion] = useState(null);
  const [alert, setAlert] = useState({show: false, message: ''});
  const [response, setResponse] = useState(null);

  // Função para mostrar o alerta
  const showAlertProcess = (message) => {
    setAlert({show: true, message});
    setTimeout(() => setAlert({show: false, message: ''}), 2000);
  };

  const showAlert = (message) => {
    setAlert({show: true, message});
  };

  const handleRestart = () => {
    window.location.reload();
  };

  // Função para limpar a rota do questionário
  const deleteQuestionario = async () => {
    try {
      const response = await fetch('http://localhost:8000/Regras/Questionario', {
        method: 'DELETE',
      });
      console.log(response);
      console.log('Rota do questionário deletada com sucesso.');
    } catch (error) {
      console.error('Erro ao deletar a rota do questionário:', error);
    }
  };
  const fetchQuestion = async () => {
    try {
      const questionsResponse = await fetch('http://localhost:8000/Regras/Questionario/get-pergunta');
      const questionsData = await questionsResponse.json();

      console.log('Pergunta obtida:', questionsData);
      setQuestion(questionsData);

    } catch (error) {
      console.error('Falha ao buscar as perguntas:', error);
      setQuestion(null);
    }
  };

  useEffect(() => {
    // Limpar a rota antes de começar o questionário
    deleteQuestionario();
    console.log('Limpando a rota do questionário...');
    if (!question){
      fetchQuestion();
    }
  }, []); // Array de dependências

  const handleAnswer = async (answer) => {
    showAlertProcess('Processando');
    try {
      console.log('Enviando resposta:', answer);
      const response = await fetch('http://localhost:8000/Regras/Questionario/post-resposta', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ txt: answer})
      }).then(response => response.json())
      console.log(response)
      if (response === 'Continua') {
        fetchQuestion();
      }
      else if (response === 'Respostas Inconclusivas'){
        showAlert('Resultado Final: ' + response);
        console.log('Resultado Final:', response);
        setResponse(response);
        deleteQuestionario();
      }
      else {
        showAlert('Resultado Final: ' + response);
        console.log('Resultado Final:', response);
        setResponse(response);
        deleteQuestionario();
      }
    } catch (error) {
      console.error('Erro ao enviar a resposta:', error);
    }
  };

  return (
    <div className="relative flex min-h-screen flex-col justify-center overflow-hidden h-14 bg-gradient-to-r from-sky-500 to-indigo-500">
      <img src="/src/img/beams.jpg" alt="" className="absolute left-1/2 top-1/2 max-w-none -translate-x-1/2 -translate-y-1/2" width="1308" />
      {alert.show && (
        <div className="absolute top-6 left-6 w-full p-10">
          {alert.show && (
            <div className="absolute top-6 left-6 w-2/2 p-4">
              <div className="bg-white text-black py-1 px-5 rounded">
                {alert.message}
              </div>
            </div>
          )}
        </div>
      )}
      <Link to="/tree" className="absolute top-4 right-4 px-2 py-1 bg-white text-black rounded" style={{ fontFamily: 'Georgia' }}>Tree</Link>
      <div className="relative bg-white px-6 pb-11 pt-11 shadow-xl ring-1 ring-gray-900/5 sm:mx-auto sm:max-w-lg sm:rounded-lg sm:px-12">
        <div className="divide-y divide-gray-300/50 text-center " style={{ fontFamily: 'Georgia', fontSize: '1.8em' }}>
          ALUFIT
        </div>
        <div style={{ fontFamily: 'font-mono', fontSize: '1.5em' }}>
          {question ? (
              <div>{question}</div>
          ) : (
            <p>Nenhuma pergunta encontrada.</p>
          )}
          {response && <div className="mt-4">Resposta: {response}</div>}
        </div>

        <div className="mt-4 flex justify-center">
          <button onClick={() => handleAnswer('Sim')} className="px-4 py-2 mr-2 bg-green-600 text-white rounded">SIM</button>
          <button onClick={() => handleAnswer('Nao')} className="px-4 py-2 mr-2 bg-red-600 text-white rounded">NÃO</button>
          <button onClick={() => handleAnswer('Nao_Sei')} className="px-4 py-2 bg-yellow-600 text-white rounded">NÃO SEI</button>

        </div>
      </div>
      <div className="flex justify-center items-center mt-4" style={{ fontFamily: 'Georgia' }}>
        <button onClick={handleRestart} className="px-4 py-2 bg-white text-black rounded">Reiniciar</button>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/tree" element={<TreePage />} />
      </Routes>
    </Router>
  );
}

export default App;
