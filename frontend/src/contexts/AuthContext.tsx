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
    login: (formData: FormData) => Promise<void>;
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
            const response = await api.get('/auth/me');
            setUser(response.data);
        } catch (error) {
            console.log('Not authenticated');
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    const login = async (formData: FormData) => {
        // FastAPI expects form data for OAuth2PasswordRequestForm
        await api.post('/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
        await checkAuth();
    };

    const logout = async () => {
        // サーバーサイドでのクッキー削除などが理想だが、現状はクライアント側で状態クリア
        // 必要に応じて /auth/logout エンドポイントを作成する
        setUser(null);
        // 簡易的にページリロードしてクリーンアップ
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
