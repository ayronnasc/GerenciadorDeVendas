import { useState, type ReactEventHandler } from 'react';
import { login } from '../services/auth';
import { useNavigate } from 'react-router-dom';

interface AuthFormData{
    name?: string;
    email: string;
    password: string;
}

export function AuthForm(){
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);

    const navigate = useNavigate();

    const [isLogin, setIsLogin] = useState<boolean>(true);

    const [formData, setFormData] = useState<AuthFormData>({
        name: '',
        email: '',
        password: '',
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const {name, value} = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        try {
            const token = await login(email, password);
            console.log('Login Successfull! Token: ', token);

            navigate('/dashboard');
        } catch (err: any){
            setError(err.message);
        }
    };

    return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-3 bg-red-100 text-red-700 text-sm rounded-lg">
          {error}
        </div>
      )}

      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Seu e-mail"
        required
        className="w-full p-2 border rounded-lg"
      />

      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Sua senha"
        required
        className="w-full p-2 border rounded-lg"
      />

      <button
        type="submit"
        className="w-full bg-blue-600 text-white p-2 rounded-lg font-bold"
      >
        Enter
      </button>
    </form>
  );
}