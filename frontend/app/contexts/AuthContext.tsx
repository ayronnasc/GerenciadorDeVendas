import { createContext, useContext, useState, useEffect } from 'react';
import { type ReactNode } from 'react';
import { api } from '../../services/index.js';

interface User{
    id: string;
    name: string;
    email: string;
}

interface AuthContextType{
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (credentials: Record<string, any>) => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: {children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() =>{
        async function checkAuthStatus() {
            try {
                const response = await api.get('/auth/me');
                setUser(response.data);
            } catch {
                setUser(null);
            } finally {
                setIsLoading(false);
            }
        }

        checkAuthStatus();
    }, []);

    const login = async (credentials: Record<string, any>) => {
        const response = await api.post('/auth/token', credentials);
        setUser(response.data.user);
    };

    const logout = async () => {
        try {
            await api.post('/auth/logout');
        } finally {
            setUser(null);
        }
    };

    return (
        <AuthContext.Provider value={{user, isAuthenticated: !!user, isLoading, login, logout}}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth must be used inside AuthProvider');
    return context;
};
