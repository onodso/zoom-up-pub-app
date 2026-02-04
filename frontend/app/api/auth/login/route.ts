import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request: Request) {
    try {
        const body = await request.json();

        const res = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });

        const data = await res.json();

        if (!res.ok) {
            return NextResponse.json(data, { status: res.status });
        }

        // Cookieにトークンを保存（HttpOnly）
        // Middlewareでアクセス制限を行うために必要
        const cookieStore = await cookies();
        cookieStore.set({
            name: 'token',
            value: data.access_token,
            httpOnly: true, // JavaScriptからアクセス不可（XSS対策）
            secure: process.env.NODE_ENV === 'production',
            path: '/',
            maxAge: 60 * 60 * 8, // 8時間
            sameSite: 'lax',
        });

        return NextResponse.json(data);
    } catch (error) {
        console.error('Login API error:', error);
        return NextResponse.json(
            { detail: '認証サーバーに接続できません' },
            { status: 503 }
        );
    }
}
