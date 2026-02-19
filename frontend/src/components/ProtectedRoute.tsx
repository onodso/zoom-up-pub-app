import React from 'react';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
    children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gray-100">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    if (!user) {
        // ログインしていない場合はログイン画面へリダイレクト
        // SPA内での遷移ではなく、完全に切り替える
        // window.location.href = '/login'; 
        // ※ App.tsxでルーティング制御するが、ここではnullを返してレンダリングさせない
        return null;
    }

    return <>{children}</>;
};
