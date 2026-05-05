'use client';

import React, { useState } from 'react';
import { Header } from '@/components/Header';
import { mockArtisans, mockServiceRequests } from '@/data/mockData';
import { ServiceRequest } from '@/types';
import { MapPin, Clock, CheckCircle, XCircle, CreditCard, Banknote, Navigation } from 'lucide-react';

export default function ArtisanDashboard() {
  const [artisan] = useState(mockArtisans[0]); // Mock logged in artisan
  const [requests, setRequests] = useState<ServiceRequest[]>(mockServiceRequests);
  const [isAvailable, setIsAvailable] = useState(artisan.isAvailable);

  const handleStatusChange = (id: string, status: ServiceRequest['status']) => {
    setRequests(requests.map(req => req.id === id ? { ...req, status } : req));
    // If starting job or en_route, mark artisan unavailable
    if (status === 'en_route' || status === 'in_progress') {
        setIsAvailable(false);
    }
  };

  const activeRequests = requests.filter(r => r.status === 'en_route' || r.status === 'in_progress' || r.status === 'accepted');
  const pendingRequests = requests.filter(r => r.status === 'pending');

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Header />

      <main className="flex-1 container mx-auto px-4 py-8 max-w-5xl">
        <div className="bg-white p-6 rounded-2xl border border-gray-200 mb-8 flex flex-col md:flex-row items-center justify-between gap-6 shadow-sm">
          <div className="flex items-center gap-4">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={artisan.avatarUrl} alt={artisan.name} className="w-16 h-16 rounded-full border-2 border-gray-100" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Welcome, {artisan.name}</h1>
              <p className="text-gray-600">{artisan.profession} • Rating: ⭐ {artisan.rating}</p>
            </div>
          </div>

          <div className="flex items-center gap-3 bg-gray-50 p-2 rounded-xl border border-gray-200">
            <span className={`text-sm font-medium ${isAvailable ? 'text-gray-600' : 'text-gray-400'}`}>Status:</span>
            <button
              onClick={() => setIsAvailable(!isAvailable)}
              className={`relative inline-flex h-8 w-16 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 ${isAvailable ? 'bg-green-500' : 'bg-gray-300'}`}
            >
              <span className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform ${isAvailable ? 'translate-x-9' : 'translate-x-1'}`} />
            </button>
            <span className={`text-sm font-bold ${isAvailable ? 'text-green-600' : 'text-gray-500'}`}>
              {isAvailable ? 'Available (On-Demand)' : 'Busy / Offline'}
            </span>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-6">

            {activeRequests.length > 0 && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Navigation className="w-5 h-5 text-blue-500" />
                  Active Job
                </h2>
                {activeRequests.map(req => (
                  <div key={req.id} className="bg-blue-50 border border-blue-200 rounded-xl p-5 mb-4 shadow-sm">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 text-xs font-bold rounded-full mb-2 uppercase tracking-wide">
                          {req.status.replace('_', ' ')}
                        </span>
                        <h3 className="font-bold text-gray-900">{req.serviceDetails}</h3>
                        <p className="text-sm text-gray-600 mt-1 flex items-center gap-1"><MapPin className="w-4 h-4"/> {req.location}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-lg">₦{req.amount.toLocaleString()}</p>
                        <p className="text-xs text-gray-500 flex items-center justify-end gap-1 mt-1">
                          {req.paymentMethod === 'cash' ? <Banknote className="w-3 h-3"/> : <CreditCard className="w-3 h-3"/>}
                          {req.paymentMethod.toUpperCase()}
                        </p>
                      </div>
                    </div>

                    <div className="flex gap-3 mt-6 pt-4 border-t border-blue-100">
                      {req.status === 'accepted' && (
                        <button onClick={() => handleStatusChange(req.id, 'en_route')} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-medium transition">
                          Start Navigation
                        </button>
                      )}
                      {req.status === 'en_route' && (
                        <button onClick={() => handleStatusChange(req.id, 'in_progress')} className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg font-medium transition">
                          Arrived (Start Job)
                        </button>
                      )}
                      {req.status === 'in_progress' && (
                        <button onClick={() => {
                          handleStatusChange(req.id, 'completed');
                          setIsAvailable(true);
                        }} className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg font-medium transition flex items-center justify-center gap-2">
                          <CheckCircle className="w-5 h-5"/> Job Completed
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-4">New Requests ({pendingRequests.length})</h2>
              {pendingRequests.length === 0 ? (
                <div className="bg-white border border-gray-200 rounded-xl p-8 text-center text-gray-500">
                  No new requests at the moment.
                </div>
              ) : (
                <div className="space-y-4">
                  {pendingRequests.map(req => (
                    <div key={req.id} className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md transition">
                      <div className="flex justify-between mb-3">
                        <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${req.bookingType === 'on-demand' ? 'bg-red-100 text-red-800' : 'bg-purple-100 text-purple-800'}`}>
                          {req.bookingType === 'on-demand' ? '🚨 ON-DEMAND NOW' : '📅 SCHEDULED'}
                        </span>
                        <span className="font-bold text-gray-900">₦{req.amount.toLocaleString()}</span>
                      </div>
                      <p className="text-gray-800 font-medium mb-3">{req.serviceDetails}</p>

                      <div className="flex items-center gap-4 text-sm text-gray-600 mb-5 bg-gray-50 p-3 rounded-lg">
                        <span className="flex items-center gap-1.5"><MapPin className="w-4 h-4 text-gray-400" /> {req.location}</span>
                        {req.bookingType === 'scheduled' && req.time && (
                          <span className="flex items-center gap-1.5"><Clock className="w-4 h-4 text-gray-400" /> {new Date(req.date).toLocaleDateString()} @ {req.time}</span>
                        )}
                      </div>

                      <div className="flex gap-3">
                        <button
                          onClick={() => handleStatusChange(req.id, 'declined')}
                          className="flex-1 flex items-center justify-center gap-2 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition"
                        >
                          <XCircle className="w-5 h-5" /> Decline
                        </button>
                        <button
                          onClick={() => handleStatusChange(req.id, req.bookingType === 'on-demand' ? 'en_route' : 'accepted')}
                          className="flex-1 flex items-center justify-center gap-2 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition"
                        >
                          <CheckCircle className="w-5 h-5" /> Accept Request
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div>
            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm sticky top-24">
              <h3 className="font-bold text-gray-900 mb-4">Earnings Overview</h3>
              <div className="space-y-4">
                <div className="bg-green-50 p-4 rounded-lg">
                  <p className="text-sm text-green-800 font-medium">Wallet Balance (Paystack)</p>
                  <p className="text-2xl font-bold text-green-900 mt-1">₦45,000</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg border border-gray-100">
                  <p className="text-sm text-gray-600 font-medium">Pending Cash Collections</p>
                  <p className="text-xl font-bold text-gray-900 mt-1">₦15,000</p>
                </div>
                <button className="w-full py-2.5 border-2 border-green-600 text-green-600 font-bold rounded-lg hover:bg-green-50 transition mt-2">
                  Withdraw Funds
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
