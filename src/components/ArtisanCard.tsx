import React from 'react';
import { Artisan } from '../types';
import { Star, MapPin, Wrench, CheckCircle } from 'lucide-react';
import { Button } from './Button';
import { Badge } from './Badge';

interface ArtisanCardProps {
  artisan: Artisan;
  onBook: (artisan: Artisan) => void;
}

export function ArtisanCard({ artisan, onBook }: ArtisanCardProps) {
  return (
    <div className="bg-apple-card rounded-3xl overflow-hidden shadow-[var(--shadow-apple)] hover:shadow-[var(--shadow-apple-hover)] transition-all duration-300 border border-gray-100">
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex gap-4">
            <div className="relative">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={artisan.avatarUrl}
                alt={artisan.name}
                className="w-16 h-16 rounded-2xl object-cover shadow-sm"
              />
              {artisan.isAvailable && (
                <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-apple-green border-2 border-white rounded-full shadow-sm"></div>
              )}
            </div>
            <div>
              <h3 className="font-semibold text-xl text-apple-text flex items-center gap-1.5 tracking-tight">
                {artisan.name}
                <CheckCircle className="w-4 h-4 text-apple-blue" />
              </h3>
              <p className="text-apple-text-secondary font-medium text-sm mt-0.5">{artisan.profession}</p>

              <div className="flex items-center gap-1 mt-1.5 text-sm text-apple-text-secondary">
                <MapPin className="w-3.5 h-3.5" />
                <span>{artisan.location} • {artisan.distance}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-5 flex items-center justify-between bg-gray-50/50 p-3 rounded-2xl">
          <div className="flex items-center gap-1.5">
            <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
            <span className="font-semibold text-apple-text">{artisan.rating}</span>
            <span className="text-apple-text-secondary text-sm">({artisan.reviews})</span>
          </div>
          <div className="font-bold text-apple-text tracking-tight">
            {artisan.price}
          </div>
        </div>

        <div className="mt-5">
          <div className="flex flex-wrap gap-2">
            {artisan.skills.slice(0, 3).map((skill, index) => (
              <Badge key={index} variant="default" className="bg-gray-100 text-gray-700 hover:bg-gray-200 border-none rounded-lg px-3 py-1 font-medium">{skill}</Badge>
            ))}
          </div>
        </div>

        <div className="mt-6">
          <Button
            fullWidth
            onClick={() => onBook(artisan)}
            disabled={!artisan.isAvailable}
          >
            {artisan.isAvailable ? 'Request Service' : 'Currently Unavailable'}
          </Button>
        </div>
      </div>
    </div>
  );
}
