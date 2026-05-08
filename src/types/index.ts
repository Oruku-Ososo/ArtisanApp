export interface Artisan {
  id: string;
  name: string;
  profession: string;
  category: string;
  rating: number;
  reviews: number;
  location: string;
  coordinates: { lat: number; lng: number }; // Added for real-time tracking MVP
  distance: string;
  price: string;
  avatarUrl: string;
  isAvailable: boolean; // false if currently on a job, true if available for on-demand
  skills: string[];
  completedJobs: number;
}

export interface User {
  id: string;
  name: string;
  email: string; // Added for Auth MVP
  location: string;
  coordinates: { lat: number; lng: number };
  avatarUrl: string;
}

export type BookingType = 'on-demand' | 'scheduled';
export type PaymentMethod = 'paystack' | 'flutterwave' | 'cash';
export type PaymentStatus = 'pending' | 'completed' | 'failed';

export interface ServiceRequest {
  id: string;
  userId: string;
  artisanId: string;
  status: 'pending' | 'accepted' | 'en_route' | 'in_progress' | 'completed' | 'declined';
  serviceDetails: string;
  location: string;
  userCoordinates: { lat: number; lng: number };
  bookingType: BookingType;
  date: string; // For scheduled, or creation time for on-demand
  time?: string; // Specific time if scheduled

  // Payment MVP
  paymentMethod: PaymentMethod;
  paymentStatus: PaymentStatus;
  amount: number;
}
