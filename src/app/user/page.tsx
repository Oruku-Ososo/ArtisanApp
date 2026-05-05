'use client';

import React, { useState } from 'react';
import { Header } from '@/components/Header';
import { ArtisanCard } from '@/components/ArtisanCard';
import { ExtendedBookingModal } from '@/components/ExtendedBookingModal';
import { mockArtisans, categories } from '@/data/mockData';
import { Artisan } from '@/types';
import { Search, Filter } from 'lucide-react';

export default function UserDashboard() {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedArtisan, setSelectedArtisan] = useState<Artisan | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const filteredArtisans = mockArtisans.filter(artisan => {
    const matchesCategory = selectedCategory === 'All' || artisan.category === selectedCategory || artisan.profession.includes(selectedCategory);
    const matchesSearch = artisan.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          artisan.profession.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          artisan.skills.some(skill => skill.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const handleBook = (artisan: Artisan) => {
    setSelectedArtisan(artisan);
    setIsModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Header />

      <main className="flex-1 container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Find an Artisan</h1>
            <p className="text-gray-600">Browse professionals near you for immediate or scheduled service.</p>
          </div>

          <div className="flex w-full md:w-auto gap-3">
            <div className="relative flex-1 md:w-72">
              <Search className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search name, trade, or skill..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 shadow-sm"
              />
            </div>
            <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50 shadow-sm">
              <Filter className="w-5 h-5" />
              <span className="hidden sm:inline">Filters</span>
            </button>
          </div>
        </div>

        <div className="mb-8 overflow-x-auto pb-2 -mx-4 px-4 sm:mx-0 sm:px-0">
          <div className="flex gap-2 min-w-max">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors whitespace-nowrap ${
                  selectedCategory === category
                    ? 'bg-gray-900 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {filteredArtisans.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredArtisans.map((artisan) => (
              <ArtisanCard
                key={artisan.id}
                artisan={artisan}
                onBook={handleBook}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-20 bg-white rounded-xl border border-gray-200 border-dashed">
            <h3 className="text-lg font-medium text-gray-900 mb-1">No artisans found</h3>
            <p className="text-gray-500">Try adjusting your search or category filter.</p>
          </div>
        )}
      </main>

      <ExtendedBookingModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        artisan={selectedArtisan}
      />
    </div>
  );
}
