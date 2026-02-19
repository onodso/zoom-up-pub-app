import axios from 'axios';

// APIクライアントの作成
// VITE_API_URL環境変数があればそれを使い、なければプロキシ設定に従う（相対パス）
// Viteの開発サーバープロキシ設定で /api へのリクエストをバックエンドへ転送することを想定
const baseURL = import.meta.env.VITE_API_BASE || import.meta.env.VITE_API_URL || '';

export const api = axios.create({
    baseURL,
    withCredentials: true, // HttpOnly Cookieの送受信に必須
    headers: {
        'Content-Type': 'application/json',
    },
});

// リクエストインターセプター：トークン自動付与
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// レスポンスインターセプター（任意）
// 401エラー時の共通処理などを追加可能
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // 401エラーはAuthContext側でハンドリングされることが多いが、
        // ここで共通処理を入れることも可能
        return Promise.reject(error);
    }
);
