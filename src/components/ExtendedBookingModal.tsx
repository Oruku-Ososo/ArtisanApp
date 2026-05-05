'use client';

import React, { useState } from 'react';
import { Artisan, BookingType, PaymentMethod } from '../types';
import { X, MapPin, Calendar, Clock, AlertCircle, Map as MapIcon, Navigation } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './Button';

interface ExtendedBookingModalProps {
  isOpen: boolean;
  onClose: () => void;
  artisan: Artisan | null;
}

export function ExtendedBookingModal({ isOpen, onClose, artisan }: ExtendedBookingModalProps) {
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1); // 1: Type, 2: Details, 3: Payment, 4: Tracking/Success
  const [bookingType, setBookingType] = useState<BookingType>('on-demand');
  const [details, setDetails] = useState('');
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>('cash');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen || !artisan) return null;

  const handleNext = () => setStep((s) => (s + 1) as 1 | 2 | 3 | 4);
  const handleBack = () => setStep((s) => (s - 1) as 1 | 2 | 3 | 4);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // Simulate API call
    setTimeout(() => {
      setIsSubmitting(false);
      setStep(4); // Move to success/tracking
    }, 1500);
  };

  const resetAndClose = () => {
    setStep(1);
    setDetails('');
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-50 backdrop-blur-sm"
            onClick={resetAndClose}
          />
          <motion.div
            initial={{ opacity: 0, y: 100, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 100, scale: 0.95 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
          >
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden pointer-events-auto flex flex-col max-h-[90vh]">
              <div className="flex items-center justify-between p-5 border-b">
                <h2 className="text-xl font-bold text-gray-900">
                  {step === 1 ? 'Booking Type' :
                   step === 2 ? 'Service Details' :
                   step === 3 ? 'Payment Method' :
                   bookingType === 'on-demand' ? 'Tracking Artisan' : 'Booking Confirmed'}
                </h2>
                {step !== 4 && (
                  <button onClick={resetAndClose} className="p-2 text-gray-500 hover:bg-gray-100 rounded-full">
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>

              <div className="p-5 overflow-y-auto">
                {step !== 4 && (
                  <div className="flex items-center gap-4 mb-6 p-4 bg-gray-50 rounded-xl">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={artisan.avatarUrl} alt={artisan.name} className="w-12 h-12 rounded-full object-cover" />
                    <div>
                      <h4 className="font-semibold text-gray-900">{artisan.name}</h4>
                      <p className="text-sm text-gray-600">{artisan.profession} • {artisan.price}</p>
                    </div>
                  </div>
                )}

                {/* Step 1: Type */}
                {step === 1 && (
                  <div className="space-y-4">
                    <button
                      onClick={() => setBookingType('on-demand')}
                      className={`w-full p-4 border-2 rounded-xl text-left transition-colors ${bookingType === 'on-demand' ? 'border-green-500 bg-green-50' : 'border-gray-200 hover:border-gray-300'}`}
                    >
                      <div className="flex items-center gap-3 mb-1">
                        <Navigation className={`w-5 h-5 ${bookingType === 'on-demand' ? 'text-green-600' : 'text-gray-400'}`} />
                        <span className="font-semibold text-gray-900">On-Demand (Now)</span>
                      </div>
                      <p className="text-sm text-gray-600 pl-8">Artisan will be dispatched to your location immediately. Best for emergencies.</p>
                    </button>

                    <button
                      onClick={() => setBookingType('scheduled')}
                      className={`w-full p-4 border-2 rounded-xl text-left transition-colors ${bookingType === 'scheduled' ? 'border-green-500 bg-green-50' : 'border-gray-200 hover:border-gray-300'}`}
                    >
                      <div className="flex items-center gap-3 mb-1">
                        <Calendar className={`w-5 h-5 ${bookingType === 'scheduled' ? 'text-green-600' : 'text-gray-400'}`} />
                        <span className="font-semibold text-gray-900">Schedule for Later</span>
                      </div>
                      <p className="text-sm text-gray-600 pl-8">Pick a specific date and time for the artisan to arrive.</p>
                    </button>
                  </div>
                )}

                {/* Step 2: Details */}
                {step === 2 && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Service Details</label>
                      <textarea
                        required
                        rows={3}
                        value={details}
                        onChange={(e) => setDetails(e.target.value)}
                        placeholder="Describe what you need help with..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none"
                      />
                    </div>

                    {bookingType === 'scheduled' && (
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
                          <div className="relative">
                            <Calendar className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
                            <input type="date" required className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none" />
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Time</label>
                          <div className="relative">
                            <Clock className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
                            <input type="time" required className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none" />
                          </div>
                        </div>
                      </div>
                    )}

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Your Location</label>
                      <div className="relative">
                        <MapPin className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" />
                        <input type="text" required defaultValue="Yaba, Lagos" className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none" />
                      </div>
                    </div>
                  </div>
                )}

                {/* Step 3: Payment */}
                {step === 3 && (
                  <div className="space-y-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">Select Payment Method</p>

                    <label className="flex items-center gap-3 p-4 border rounded-xl cursor-pointer hover:bg-gray-50">
                      <input type="radio" name="payment" checked={paymentMethod === 'cash'} onChange={() => setPaymentMethod('cash')} className="w-4 h-4 text-green-600 focus:ring-green-500" />
                      <span className="font-medium">Cash on Delivery (Trackable)</span>
                    </label>
                    <label className="flex items-center gap-3 p-4 border rounded-xl cursor-pointer hover:bg-gray-50">
                      <input type="radio" name="payment" checked={paymentMethod === 'paystack'} onChange={() => setPaymentMethod('paystack')} className="w-4 h-4 text-green-600 focus:ring-green-500" />
                      <span className="font-medium">Card/Transfer via Paystack</span>
                    </label>
                    <label className="flex items-center gap-3 p-4 border rounded-xl cursor-pointer hover:bg-gray-50">
                      <input type="radio" name="payment" checked={paymentMethod === 'flutterwave'} onChange={() => setPaymentMethod('flutterwave')} className="w-4 h-4 text-green-600 focus:ring-green-500" />
                      <span className="font-medium">Card/Transfer via Flutterwave</span>
                    </label>
                  </div>
                )}

                {/* Step 4: Tracking / Success */}
                {step === 4 && (
                  <div className="flex flex-col items-center text-center py-6">
                    {bookingType === 'on-demand' ? (
                      <>
                        <div className="w-full h-48 bg-gray-200 rounded-xl mb-6 relative overflow-hidden flex items-center justify-center border">
                          <MapIcon className="w-12 h-12 text-gray-400" />
                          <div className="absolute inset-0 bg-blue-50/50 backdrop-blur-[1px]"></div>
                          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
                            <Navigation className="w-8 h-8 text-blue-600 animate-pulse" />
                            <span className="text-sm font-bold text-blue-800 mt-2 bg-white px-2 py-1 rounded shadow-sm">Artisan is 1.2km away</span>
                          </div>
                        </div>
                        <h3 className="text-2xl font-bold text-gray-900 mb-2">Artisan is En Route!</h3>
                        <p className="text-gray-600 mb-6">{artisan.name} has accepted your request and is heading to your location.</p>
                      </>
                    ) : (
                      <>
                        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-6 mx-auto">
                          <AlertCircle className="w-8 h-8 text-green-600" />
                        </div>
                        <h3 className="text-2xl font-bold text-gray-900 mb-2">Booking Scheduled!</h3>
                        <p className="text-gray-600 mb-6">Your appointment with {artisan.name} is confirmed.</p>
                      </>
                    )}
                    <Button onClick={resetAndClose} className="w-full">Back to Dashboard</Button>
                  </div>
                )}
              </div>

              {step !== 4 && (
                <div className="p-4 border-t bg-gray-50 flex justify-between">
                  {step > 1 ? (
                    <Button type="button" variant="outline" onClick={handleBack}>Back</Button>
                  ) : <div></div>}

                  {step < 3 ? (
                    <Button type="button" onClick={handleNext}>Next Step</Button>
                  ) : (
                    <Button type="button" onClick={handleSubmit} disabled={isSubmitting}>
                      {isSubmitting ? 'Processing...' : 'Confirm Booking'}
                    </Button>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
