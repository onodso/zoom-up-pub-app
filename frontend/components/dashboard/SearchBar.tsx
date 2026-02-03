'use client';

import { useState } from 'react';

interface SearchBarProps {
    onSearch: (query: string) => void;
    placeholder?: string;
}

export default function SearchBar({ onSearch, placeholder = '自治体名で検索...' }: SearchBarProps) {
    const [query, setQuery] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSearch(query);
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setQuery(value);
        onSearch(value); // リアルタイム検索
    };

    const handleClear = () => {
        setQuery('');
        onSearch('');
    };

    return (
        <form onSubmit={handleSubmit} className="relative">
            <div className="relative">
                {/* 検索アイコン */}
                <svg
                    className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                </svg>

                {/* 入力フィールド */}
                <input
                    type="text"
                    value={query}
                    onChange={handleChange}
                    placeholder={placeholder}
                    className="w-full pl-14 pr-12 py-4 text-lg bg-white rounded-2xl shadow-lg border border-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />

                {/* クリアボタン */}
                {query && (
                    <button
                        type="button"
                        onClick={handleClear}
                        className="absolute right-5 top-1/2 -translate-y-1/2 w-6 h-6 flex items-center justify-center text-gray-400 hover:text-gray-600 transition-colors"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                )}
            </div>

            {/* 検索ヒント */}
            <div className="mt-2 flex gap-2 px-2">
                <span className="text-xs text-gray-400">クイック検索:</span>
                {['渋谷', '横浜', '名古屋'].map((hint) => (
                    <button
                        key={hint}
                        type="button"
                        onClick={() => {
                            setQuery(hint);
                            onSearch(hint);
                        }}
                        className="text-xs text-blue-500 hover:text-blue-700 hover:underline transition-colors"
                    >
                        {hint}
                    </button>
                ))}
            </div>
        </form>
    );
}
