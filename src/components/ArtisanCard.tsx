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
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300">
      <div className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex gap-4">
            <div className="relative">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={artisan.avatarUrl}
                alt={artisan.name}
                className="w-16 h-16 rounded-full object-cover border-2 border-gray-100"
              />
              {artisan.isAvailable && (
                <div className="absolute bottom-0 right-0 w-4 h-4 bg-green-500 border-2 border-white rounded-full"></div>
              )}
            </div>
            <div>
              <h3 className="font-semibold text-lg text-gray-900 flex items-center gap-1">
                {artisan.name}
                <CheckCircle className="w-4 h-4 text-blue-500" />
              </h3>
              <p className="text-gray-600 font-medium text-sm">{artisan.profession}</p>

              <div className="flex items-center gap-1 mt-1 text-sm text-gray-500">
                <MapPin className="w-3.5 h-3.5" />
                <span>{artisan.location} • {artisan.distance}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4 flex items-center justify-between">
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
            <span className="font-semibold text-gray-900">{artisan.rating}</span>
            <span className="text-gray-500 text-sm">({artisan.reviews} reviews)</span>
          </div>
          <div className="font-semibold text-gray-900">
            {artisan.price}
          </div>
        </div>

        <div className="mt-4">
          <div className="flex items-center gap-1.5 mb-2 text-sm text-gray-700 font-medium">
            <Wrench className="w-4 h-4 text-gray-500" />
            <span>Top Skills</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {artisan.skills.slice(0, 3).map((skill, index) => (
              <Badge key={index} variant="default">{skill}</Badge>
            ))}
          </div>
        </div>

        <div className="mt-5">
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
