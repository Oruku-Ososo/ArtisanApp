'use client';

import React, { useState } from 'react';
import { Header } from '@/components/Header';
import { mockArtisans, mockServiceRequests } from '@/data/mockData';
import { ServiceRequest } from '@/types';
import { MapPin, Clock, CheckCircle, XCircle, CreditCard, Banknote, Navigation } from 'lucide-react';
import { motion } from 'framer-motion';

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
    <div className="min-h-screen bg-apple-bg flex flex-col">
      <Header />

      <main className="flex-1 container mx-auto px-4 py-8 max-w-5xl">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6 rounded-3xl mb-8 flex flex-col md:flex-row items-center justify-between gap-6 shadow-sm border border-gray-200/50"
        >
          <div className="flex items-center gap-4">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={artisan.avatarUrl} alt={artisan.name} className="w-16 h-16 rounded-2xl shadow-sm" />
            <div>
              <h1 className="text-2xl font-bold text-apple-text tracking-tight">Welcome, {artisan.name}</h1>
              <p className="text-apple-text-secondary mt-0.5">{artisan.profession} • ⭐ {artisan.rating}</p>
            </div>
          </div>

          <div className="flex items-center gap-4 bg-white/50 p-2.5 rounded-2xl border border-gray-100">
            <span className={`text-sm font-medium ${isAvailable ? 'text-apple-text' : 'text-apple-text-secondary'}`}>Status:</span>
            <button
              onClick={() => setIsAvailable(!isAvailable)}
              className={`relative inline-flex h-8 w-14 items-center rounded-full transition-colors focus:outline-none ${isAvailable ? 'bg-apple-green' : 'bg-gray-300'}`}
            >
              <span className={`inline-block h-6 w-6 transform rounded-full bg-white shadow-sm transition-transform ${isAvailable ? 'translate-x-7' : 'translate-x-1'}`} />
            </button>
            <span className={`text-sm font-semibold min-w-[140px] ${isAvailable ? 'text-apple-green' : 'text-gray-500'}`}>
              {isAvailable ? 'Available (Active)' : 'Busy / Offline'}
            </span>
          </div>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-8">

            {activeRequests.length > 0 && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <h2 className="text-xl font-bold text-apple-text mb-4 flex items-center gap-2 tracking-tight">
                  <Navigation className="w-5 h-5 text-apple-blue" />
                  Active Job
                </h2>
                {activeRequests.map(req => (
                  <div key={req.id} className="bg-blue-50/50 border border-blue-100 rounded-3xl p-6 mb-4 shadow-sm backdrop-blur-sm">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <span className="inline-block px-3 py-1 bg-blue-100 text-apple-blue text-xs font-bold rounded-full mb-3 uppercase tracking-wider">
                          {req.status.replace('_', ' ')}
                        </span>
                        <h3 className="font-semibold text-lg text-apple-text">{req.serviceDetails}</h3>
                        <p className="text-sm text-apple-text-secondary mt-1.5 flex items-center gap-1.5"><MapPin className="w-4 h-4"/> {req.location}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-xl text-apple-text">₦{req.amount.toLocaleString()}</p>
                        <p className="text-xs text-apple-text-secondary flex items-center justify-end gap-1 mt-1 font-medium">
                          {req.paymentMethod === 'cash' ? <Banknote className="w-3.5 h-3.5"/> : <CreditCard className="w-3.5 h-3.5"/>}
                          {req.paymentMethod.toUpperCase()}
                        </p>
                      </div>
                    </div>

                    <div className="flex gap-3 mt-6 pt-5 border-t border-blue-100/50">
                      {req.status === 'accepted' && (
                        <button onClick={() => handleStatusChange(req.id, 'en_route')} className="flex-1 bg-apple-blue hover:bg-apple-blue-hover text-white py-3 rounded-2xl font-semibold transition-all active:scale-[0.98] shadow-sm">
                          Start Navigation
                        </button>
                      )}
                      {req.status === 'en_route' && (
                        <button onClick={() => handleStatusChange(req.id, 'in_progress')} className="flex-1 bg-apple-blue hover:bg-apple-blue-hover text-white py-3 rounded-2xl font-semibold transition-all active:scale-[0.98] shadow-sm">
                          Arrived (Start Job)
                        </button>
                      )}
                      {req.status === 'in_progress' && (
                        <button onClick={() => {
                          handleStatusChange(req.id, 'completed');
                          setIsAvailable(true);
                        }} className="flex-1 bg-apple-green hover:bg-apple-green-hover text-white py-3 rounded-2xl font-semibold transition-all active:scale-[0.98] flex items-center justify-center gap-2 shadow-sm">
                          <CheckCircle className="w-5 h-5"/> Job Completed
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </motion.div>
            )}

            <div>
              <h2 className="text-xl font-bold text-apple-text mb-4 tracking-tight">New Requests ({pendingRequests.length})</h2>
              {pendingRequests.length === 0 ? (
                <div className="bg-apple-card border border-gray-200/50 rounded-3xl p-10 text-center text-apple-text-secondary shadow-[var(--shadow-apple)]">
                  No new requests at the moment.
                </div>
              ) : (
                <div className="space-y-4">
                  {pendingRequests.map(req => (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      key={req.id}
                      className="bg-apple-card border border-gray-100 rounded-3xl p-6 shadow-[var(--shadow-apple)] hover:shadow-[var(--shadow-apple-hover)] transition-all"
                    >
                      <div className="flex justify-between items-start mb-3">
                        <span className={`text-xs font-bold px-3 py-1.5 rounded-full tracking-wide ${req.bookingType === 'on-demand' ? 'bg-red-50 text-red-600' : 'bg-purple-50 text-purple-600'}`}>
                          {req.bookingType === 'on-demand' ? '🚨 ON-DEMAND' : '📅 SCHEDULED'}
                        </span>
                        <span className="font-bold text-lg text-apple-text">₦{req.amount.toLocaleString()}</span>
                      </div>
                      <p className="text-apple-text font-medium mb-4">{req.serviceDetails}</p>

                      <div className="flex flex-col gap-2 text-sm text-apple-text-secondary mb-6 bg-gray-50/50 p-3.5 rounded-2xl">
                        <span className="flex items-center gap-2"><MapPin className="w-4 h-4 text-gray-400" /> {req.location}</span>
                        {req.bookingType === 'scheduled' && req.time && (
                          <span className="flex items-center gap-2"><Clock className="w-4 h-4 text-gray-400" /> {new Date(req.date).toLocaleDateString()} @ {req.time}</span>
                        )}
                      </div>

                      <div className="flex gap-3">
                        <button
                          onClick={() => handleStatusChange(req.id, 'declined')}
                          className="flex-1 flex items-center justify-center gap-2 py-3 bg-gray-100 text-gray-700 rounded-2xl hover:bg-gray-200 font-semibold transition-all active:scale-[0.98]"
                        >
                          <XCircle className="w-5 h-5" /> Decline
                        </button>
                        <button
                          onClick={() => handleStatusChange(req.id, req.bookingType === 'on-demand' ? 'en_route' : 'accepted')}
                          className="flex-1 flex items-center justify-center gap-2 py-3 bg-apple-green text-white rounded-2xl hover:bg-apple-green-hover font-semibold transition-all active:scale-[0.98] shadow-sm"
                        >
                          <CheckCircle className="w-5 h-5" /> Accept
                        </button>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div>
            <div className="bg-apple-card border border-gray-100 rounded-3xl p-6 shadow-[var(--shadow-apple)] sticky top-24">
              <h3 className="font-bold text-apple-text mb-5 tracking-tight">Earnings Overview</h3>
              <div className="space-y-4">
                <div className="bg-green-50/50 p-5 rounded-2xl">
                  <p className="text-sm text-green-700 font-medium">Wallet Balance (Paystack)</p>
                  <p className="text-3xl font-bold text-apple-green mt-1 tracking-tight">₦45,000</p>
                </div>
                <div className="bg-gray-50/50 p-5 rounded-2xl border border-gray-100/50">
                  <p className="text-sm text-apple-text-secondary font-medium">Pending Cash Collections</p>
                  <p className="text-2xl font-bold text-apple-text mt-1 tracking-tight">₦15,000</p>
                </div>
                <button className="w-full py-3.5 bg-gray-100 text-apple-text font-semibold rounded-2xl hover:bg-gray-200 transition-all active:scale-[0.98] mt-2">
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
