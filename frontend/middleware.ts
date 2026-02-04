import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
    // 現在のパス
    const path = request.nextUrl.pathname;
    console.log(`[Middleware] Accessing: ${path}`);


    // パブリックパス（認証不要なパス）
    const publicPaths = ['/login', '/api/auth/login'];
    if (publicPaths.some(p => path.startsWith(p))) {
        return NextResponse.next();
    }

    // 静的ファイルとAPIルートの一部は除外
    if (
        path.startsWith('/_next') ||
        path.startsWith('/favicon.ico') ||
        path.match(/\.(png|jpg|jpeg|gif|svg|css|js)$/)
    ) {
        return NextResponse.next();
    }

    // トークンチェック
    const token = request.cookies.get('token')?.value;

    if (!token) {
        // トークンがない場合はログインページへリダイレクト
        return NextResponse.redirect(new URL('/login', request.url));
    }

    return NextResponse.next();
}

export const config = {
    matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
