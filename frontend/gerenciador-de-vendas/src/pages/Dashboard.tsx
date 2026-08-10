export function DashboardPage() {
  const handleLogout = () => {
    localStorage.removeItem('token'); // Apaga o token
    window.location.href = '/'; // Volta pro login
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Painel de Vendas</h1>
      <p className="mb-4">Bem-vindo ao sistema de gerenciamento!</p>
      
      <button 
        onClick={handleLogout}
        className="px-4 py-2 bg-red-600 text-white rounded-lg"
      >
        Sair
      </button>
    </div>
  );
}