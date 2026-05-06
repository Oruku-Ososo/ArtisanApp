'use client';

import React, { useState } from 'react';
import { Header } from '@/components/Header';
import { ArtisanCard } from '@/components/ArtisanCard';
import { ExtendedBookingModal } from '@/components/ExtendedBookingModal';
import { mockArtisans, categories } from '@/data/mockData';
import { Artisan } from '@/types';
import { Search, Filter } from 'lucide-react';

import { motion, AnimatePresence } from 'framer-motion';

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
    <div className="min-h-screen bg-apple-bg flex flex-col">
      <Header />

      <main className="flex-1 container mx-auto px-4 py-8 max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-6"
        >
          <div>
            <h1 className="text-4xl font-bold text-apple-text tracking-tight mb-2">Find an Artisan</h1>
            <p className="text-apple-text-secondary text-lg">Browse professionals near you for immediate or scheduled service.</p>
          </div>

          <div className="flex w-full md:w-auto gap-3">
            <div className="relative flex-1 md:w-80">
              <Search className="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search name, trade, or skill..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-11 pr-4 py-3 bg-white border-none rounded-2xl focus:outline-none focus:ring-2 focus:ring-apple-blue shadow-sm transition-shadow text-base"
              />
            </div>
            <button className="flex items-center gap-2 px-5 py-3 bg-white rounded-2xl text-gray-700 hover:bg-gray-50 shadow-sm transition-all active:scale-[0.98]">
              <Filter className="w-5 h-5" />
              <span className="hidden sm:inline font-medium">Filters</span>
            </button>
          </div>
        </motion.div>

        <div className="mb-10 overflow-x-auto pb-4 hide-scrollbar -mx-4 px-4 sm:mx-0 sm:px-0">
          <div className="flex gap-2 min-w-max p-1 bg-gray-200/50 rounded-full w-fit">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-5 py-2.5 rounded-full text-sm font-medium transition-all whitespace-nowrap shadow-sm ${
                  selectedCategory === category
                    ? 'bg-white text-apple-text scale-100'
                    : 'bg-transparent text-gray-500 hover:text-gray-900 shadow-none scale-95 hover:scale-100'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {filteredArtisans.length > 0 ? (
          <motion.div
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ staggerChildren: 0.1 }}
          >
            {filteredArtisans.map((artisan, index) => (
              <motion.div
                key={artisan.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <ArtisanCard
                  artisan={artisan}
                  onBook={handleBook}
                />
              </motion.div>
            ))}
          </motion.div>
        ) : (
          <div className="text-center py-24 bg-white rounded-3xl border-2 border-gray-100 border-dashed shadow-sm">
            <h3 className="text-xl font-semibold text-apple-text mb-2">No artisans found</h3>
            <p className="text-apple-text-secondary">Try adjusting your search or category filter.</p>
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
