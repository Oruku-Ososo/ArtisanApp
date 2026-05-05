import React from 'react';
import Link from 'next/link';
import { Menu, User, Bell } from 'lucide-react';

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button className="md:hidden p-2 -ml-2 text-gray-600 hover:bg-gray-100 rounded-md">
            <Menu className="w-5 h-5" />
          </button>
          <Link href="/" className="font-bold text-xl text-green-700 tracking-tight flex items-center gap-2">
            <span className="w-8 h-8 bg-green-600 text-white flex items-center justify-center rounded-md font-bold">O</span>
            OgaArtisan
          </Link>
        </div>

        <nav className="hidden md:flex items-center gap-6">
          <Link href="/" className="text-sm font-medium text-gray-600 hover:text-gray-900">Home</Link>
          <Link href="/user" className="text-sm font-medium text-gray-600 hover:text-gray-900">Find Artisan</Link>
          <Link href="/artisan" className="text-sm font-medium text-gray-600 hover:text-gray-900">Artisan Dashboard</Link>
        </nav>

        <div className="flex items-center gap-4">
          <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-full relative">
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
          <Link href="/login">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center overflow-hidden border border-gray-300 hover:bg-gray-300 cursor-pointer">
              <User className="w-5 h-5 text-gray-600" />
            </div>
          </Link>
        </div>
      </div>
    </header>
  );
}
