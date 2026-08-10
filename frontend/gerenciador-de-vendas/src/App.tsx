import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthForm } from './components/AuthForm';

// Componente simples para testar o Dashboard
function Dashboard() {
  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto bg-white p-6 rounded-xl shadow-md">
        <h1 className="text-2xl font-bold text-gray-800">Painel de Vendas</h1>
        <p className="text-gray-600 mt-2">Você está autenticado no sistema!</p>
        
        <button
          onClick={handleLogout}
          className="mt-6 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition"
        >
          Sair
        </button>
      </div>
    </div>
  );
}

export function App() {
  // Função que checa se existe um token salvo
  const estaAutenticado = () => {
    return !!localStorage.getItem('token');
  };

  return (
    <BrowserRouter>
      <Routes>
        {/* Tela Principal / Login */}
        <Route path="/" element={<AuthForm />} />

        {/* Rota Protegida do Dashboard */}
        <Route
          path="/dashboard"
          element={
            estaAutenticado() ? <Dashboard /> : <Navigate to="/" replace />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;