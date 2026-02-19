import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../api/client';

interface User {
    email: string;
    name: string;
    role: string;
    assigned_regions: string[];
}

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (data: { email: string; password: string }) => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    // 初回ロード時にセッションチェック
    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const response = await api.get('/api/auth/me');
            setUser(response.data);
        } catch (error) {
            console.log('Not authenticated');
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    const login = async (data: { email: string; password: string }) => {
        const response = await api.post('/api/auth/login', data);
        if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token);
        }
        await checkAuth();
    };

    const logout = async () => {
        localStorage.removeItem('token');
        setUser(null);
        window.location.href = '/login';
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
