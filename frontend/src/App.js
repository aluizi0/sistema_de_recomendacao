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

  // Função para limpar a rota do questionário
  const deleteQuestionario = async () => {
    try {
      await fetch('http://localhost:8000/Regras/Questionario', {
        method: 'DELETE',
      });
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
    console.log('Limpando a rota do questionário...');
    if (!question){
      fetchQuestion();
    }
  }, []); // Array de dependências

  const handleAnswer = async (answer) => {
    try {
      console.log('Enviando resposta:', answer);
      const response = await fetch('http://localhost:8000/Regras/Questionario/post-resposta', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ txt: answer})
      });
  
      if (response.ok) {
        const responseData = await response.text();
  
        if (responseData === 'Continua') {
          const questionResponse = await fetch('http://localhost:8000/Regras/Questionario/get-pergunta');
  
          if (questionResponse.ok) {
            const questionData = await questionResponse.json();
            setQuestion(questionData);
          } else {
            console.error('Erro ao obter a próxima pergunta:', questionResponse.status);
          }
        } else {
          console.log('Resultado Final:', responseData);
        }
      } else {
        console.error('Erro ao enviar a resposta:', response.status);
      }
    } catch (error) {
      console.error('Erro ao enviar a resposta:', error);
    }
  };

  return (
    <div className="relative flex min-h-screen flex-col justify-center overflow-hidden bg-gray-50 py-6 sm:py-12">
      <img src="/img/beams.jpg" alt="" className="absolute left-1/2 top-1/2 max-w-none -translate-x-1/2 -translate-y-1/2" width="1308" />
      <Link to="/tree" className="absolute top-4 right-4 px-2 py-1 bg-blue-600 text-white rounded">Tree</Link>
      <div className="relative bg-white px-6 pb-8 pt-10 shadow-xl ring-1 ring-gray-900/5 sm:mx-auto sm:max-w-lg sm:rounded-lg sm:px-10">
        <div className="divide-y divide-gray-300/50 text-center " style={{ fontFamily: 'Georgia', fontSize: '1.8em' }}>
          ALUFIT
        </div>
        <div>
          {question ? (
              <div>{question}</div>
          ) : (
            <p>Nenhuma pergunta encontrada.</p>
          )}
        </div>
        <div className="mt-4">
          <button onClick={() => handleAnswer('Sim')} className="px-4 py-2 mr-2 bg-green-600 text-white rounded">SIM</button>
          <button onClick={() => handleAnswer('Nao')} className="px-4 py-2 mr-2 bg-red-600 text-white rounded">NÃO</button>
          <button onClick={() => handleAnswer('Nao_Sei')} className="px-4 py-2 bg-yellow-600 text-white rounded">NÃO SEI</button>

        </div>
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
