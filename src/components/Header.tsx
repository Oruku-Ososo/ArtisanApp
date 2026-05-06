import React from 'react';
import Link from 'next/link';
import { Menu, User, Bell } from 'lucide-react';

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full glass">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button className="md:hidden p-2 -ml-2 text-gray-600 hover:bg-gray-100 rounded-xl transition-colors">
            <Menu className="w-5 h-5" />
          </button>
          <Link href="/" className="font-semibold text-xl text-apple-text tracking-tight flex items-center gap-2">
            <span className="w-8 h-8 bg-apple-text text-white flex items-center justify-center rounded-xl font-bold">O</span>
            OgaArtisan
          </Link>
        </div>

        <nav className="hidden md:flex items-center gap-1 bg-gray-100/50 p-1 rounded-full">
          <Link href="/" className="text-sm font-medium text-gray-600 hover:text-apple-text hover:bg-white px-4 py-1.5 rounded-full transition-all">Home</Link>
          <Link href="/user" className="text-sm font-medium text-gray-600 hover:text-apple-text hover:bg-white px-4 py-1.5 rounded-full transition-all">Find Artisan</Link>
          <Link href="/artisan" className="text-sm font-medium text-gray-600 hover:text-apple-text hover:bg-white px-4 py-1.5 rounded-full transition-all">Artisan Dashboard</Link>
        </nav>

        <div className="flex items-center gap-4">
          <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-full relative transition-colors">
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
          </button>
          <Link href="/login">
            <div className="w-9 h-9 bg-gray-100 rounded-full flex items-center justify-center overflow-hidden hover:bg-gray-200 transition-colors cursor-pointer">
              <User className="w-5 h-5 text-gray-600" />
            </div>
          </Link>
        </div>
      </div>
    </header>
  );
}
