import { Artisan, User, ServiceRequest } from '../types';

export const categories = [
  'All',
  'Automobile Mechanics',
  'Hairdressers',
  'Tailors and Dressmakers',
  'Plumbers and Pipe Fitters',
  'Electricians',
  'Carpenters and Joiners',
  'Masons',
  'Painters and Decorators',
  'Welders',
  'Computer Hardware Technicians',
  'Beauty Therapists'
];

export const allCategoriesList = {
  "Construction and Building Trades": [
    "Carpenters and Joiners",
    "Painters and Decorators",
    "Plasterers",
    "Plumbers and Pipe Fitters",
    "Steel Fixers and Steel Benders",
    "Masons",
    "Aluminium Fabricators",
    "POP (Plaster of Paris) Installers"
  ],
  "Automotive and Mechanical Trades": [
    "Automobile Mechanics",
    "Motor Vehicle Electricians",
    "Auto Body Repair Technicians and Vehicle Painters",
    "Motorcycle and Tricycle Repair Technicians",
    "Automobile LPG/CNG Conversion Mechanics",
    "Diesel Mechanics",
    "Fitters and Turners",
    "Welders"
  ],
  "Electrical and Electronics Trades": [
    "Electricians",
    "Telecommunications Technicians",
    "Solar Photovoltaic (PV) Installers",
    "Computer Hardware and GSM Repair Technicians",
    "Refrigeration and Air Conditioning (RAC) Mechanics",
    "Fiber-Optic Splicers"
  ],
  "Personal Care, Beauty, and Hospitality Trades": [
    "Hairdressers (Men's and Women's)",
    "Nail Technicians",
    "Makeup Artists",
    "Beauty Therapists",
    "Chefs and Cooks",
    "Bakers",
    "Tour Guides"
  ],
  "Apparel and Textile Trades": [
    "Tailors and Dressmakers",
    "Shoe Makers (Cordwainers)",
    "Leather Workers",
    "Beadmakers",
    "Fashion Designers"
  ],
  "Industrial, Advanced Technical, and Emerging Trades": [
    "Boilermakers",
    "Millwrights",
    "Toolmakers",
    "Riggers",
    "Patternmakers",
    "Metal Machinists",
    "Mechatronics Technicians"
  ],
  "Additional Trades": [
    "Furniture Makers and Upholsterers",
    "Cabinet Makers",
    "Commercial Refrigeration Mechanics",
    "Cybersecurity Hardware Installers",
    "Leather Craft Workers",
    "Upholsterers / Shoe Repairers"
  ]
};

export const mockArtisans: Artisan[] = [
  {
    id: 'a1',
    name: 'Chinedu Okeke',
    profession: 'Automobile Mechanics',
    category: 'Automotive and Mechanical Trades',
    rating: 4.8,
    reviews: 124,
    location: 'Surulere, Lagos',
    coordinates: { lat: 6.4975, lng: 3.3512 },
    distance: '1.2 km away',
    price: '₦5000/hr',
    avatarUrl: 'https://i.pravatar.cc/150?img=11',
    isAvailable: true,
    skills: ['Engine Repair', 'Brake Replacement', 'General Servicing'],
    completedJobs: 340,
  },
  {
    id: 'a2',
    name: 'Aisha Bello',
    profession: 'Hairdressers (Men\'s and Women\'s)',
    category: 'Personal Care, Beauty, and Hospitality Trades',
    rating: 4.9,
    reviews: 89,
    location: 'Wuse, Abuja',
    coordinates: { lat: 9.0765, lng: 7.3986 },
    distance: '3.5 km away',
    price: '₦8000/session',
    avatarUrl: 'https://i.pravatar.cc/150?img=5',
    isAvailable: true,
    skills: ['Braiding', 'Weaving', 'Natural Hair Styling'],
    completedJobs: 210,
  },
  {
    id: 'a3',
    name: 'Oluwaseun Adeyemi',
    profession: 'Masons',
    category: 'Construction and Building Trades',
    rating: 4.5,
    reviews: 56,
    location: 'Ikeja, Lagos',
    coordinates: { lat: 6.6018, lng: 3.3515 },
    distance: '5.0 km away',
    price: '₦10000/day',
    avatarUrl: 'https://i.pravatar.cc/150?img=12',
    isAvailable: false,
    skills: ['Block Laying', 'Plastering', 'Concrete Work'],
    completedJobs: 150,
  },
  {
    id: 'a4',
    name: 'Ngozi Eze',
    profession: 'Tailors and Dressmakers',
    category: 'Apparel and Textile Trades',
    rating: 4.7,
    reviews: 205,
    location: 'Garki, Abuja',
    coordinates: { lat: 9.0333, lng: 7.4833 },
    distance: '2.0 km away',
    price: '₦15000/dress',
    avatarUrl: 'https://i.pravatar.cc/150?img=9',
    isAvailable: true,
    skills: ['Ankara Styles', 'Aso-ebi', 'Ready-to-wear'],
    completedJobs: 420,
  },
  {
    id: 'a5',
    name: 'Emeka Uzo',
    profession: 'Carpenters and Joiners',
    category: 'Construction and Building Trades',
    rating: 4.6,
    reviews: 78,
    location: 'Lekki, Lagos',
    coordinates: { lat: 6.4698, lng: 3.5852 },
    distance: '8.2 km away',
    price: '₦3000/sqm',
    avatarUrl: 'https://i.pravatar.cc/150?img=15',
    isAvailable: true,
    skills: ['Woodwork', 'Furniture Repair', 'Roofing Framework'],
    completedJobs: 185,
  },
  {
    id: 'a6',
    name: 'Tunde Bakare',
    profession: 'Plumbers and Pipe Fitters',
    category: 'Construction and Building Trades',
    rating: 4.9,
    reviews: 312,
    location: 'Yaba, Lagos',
    coordinates: { lat: 6.5050, lng: 3.3750 },
    distance: '0.8 km away',
    price: '₦4000/hr',
    avatarUrl: 'https://i.pravatar.cc/150?img=13',
    isAvailable: true,
    skills: ['Pipe Fitting', 'Leak Repair', 'Water Heater Installation'],
    completedJobs: 560,
  }
];

export const mockUser: User = {
  id: 'u1',
  name: 'Femi Johnson',
  email: 'femi.johnson@example.com',
  location: 'Yaba, Lagos',
  coordinates: { lat: 6.5055, lng: 3.3755 },
  avatarUrl: 'https://i.pravatar.cc/150?img=33',
};

export const mockServiceRequests: ServiceRequest[] = [
  {
    id: 'sr1',
    userId: 'u1',
    artisanId: 'a1',
    status: 'en_route',
    serviceDetails: 'My car engine is making a knocking sound and wont start. I am stuck on the road.',
    location: 'Yaba, Lagos',
    userCoordinates: { lat: 6.5055, lng: 3.3755 },
    bookingType: 'on-demand',
    date: new Date().toISOString(),
    paymentMethod: 'cash',
    paymentStatus: 'pending',
    amount: 15000
  },
  {
    id: 'sr2',
    userId: 'u2',
    artisanId: 'a1',
    status: 'accepted',
    serviceDetails: 'Need a full car servicing and oil change tomorrow.',
    location: 'Surulere, Lagos',
    userCoordinates: { lat: 6.4970, lng: 3.3510 },
    bookingType: 'scheduled',
    date: '2023-11-16',
    time: '14:00',
    paymentMethod: 'paystack',
    paymentStatus: 'completed',
    amount: 25000
  }
];
