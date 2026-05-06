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
            className="fixed inset-0 bg-black/40 z-40 backdrop-blur-md"
            onClick={resetAndClose}
          />
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.97 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
          >
            <div className="bg-apple-card rounded-[32px] shadow-[var(--shadow-apple-modal)] w-full max-w-md pointer-events-auto flex flex-col max-h-[90vh] border border-white/20">
              <div className="flex items-center justify-between p-6 border-b border-gray-100/50 bg-white/50 rounded-t-[32px] backdrop-blur-sm">
                <h2 className="text-xl font-bold text-apple-text tracking-tight">
                  {step === 1 ? 'Booking Type' :
                   step === 2 ? 'Service Details' :
                   step === 3 ? 'Payment Method' :
                   bookingType === 'on-demand' ? 'Tracking Artisan' : 'Booking Confirmed'}
                </h2>
                {step !== 4 && (
                  <button onClick={resetAndClose} className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors">
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>

              <div className="p-6 overflow-y-auto">
                {step !== 4 && (
                  <div className="flex items-center gap-4 mb-8 p-4 bg-gray-50/80 rounded-2xl border border-gray-100">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={artisan.avatarUrl} alt={artisan.name} className="w-14 h-14 rounded-2xl object-cover shadow-sm" />
                    <div>
                      <h4 className="font-bold text-apple-text text-lg tracking-tight">{artisan.name}</h4>
                      <p className="text-sm text-apple-text-secondary font-medium">{artisan.profession} • {artisan.price}</p>
                    </div>
                  </div>
                )}

                {/* Step 1: Type */}
                {step === 1 && (
                  <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-4">
                    <button
                      onClick={() => setBookingType('on-demand')}
                      className={`w-full p-5 border-2 rounded-2xl text-left transition-all active:scale-[0.98] ${bookingType === 'on-demand' ? 'border-apple-green bg-green-50/30 shadow-sm' : 'border-gray-100 hover:border-gray-200'}`}
                    >
                      <div className="flex items-center gap-3 mb-1.5">
                        <div className={`p-2 rounded-xl ${bookingType === 'on-demand' ? 'bg-apple-green text-white' : 'bg-gray-100 text-gray-500'}`}>
                          <Navigation className="w-5 h-5" />
                        </div>
                        <span className="font-bold text-apple-text text-lg">On-Demand (Now)</span>
                      </div>
                      <p className="text-sm text-apple-text-secondary pl-[52px]">Artisan will be dispatched to your location immediately. Best for emergencies.</p>
                    </button>

                    <button
                      onClick={() => setBookingType('scheduled')}
                      className={`w-full p-5 border-2 rounded-2xl text-left transition-all active:scale-[0.98] ${bookingType === 'scheduled' ? 'border-apple-green bg-green-50/30 shadow-sm' : 'border-gray-100 hover:border-gray-200'}`}
                    >
                      <div className="flex items-center gap-3 mb-1.5">
                        <div className={`p-2 rounded-xl ${bookingType === 'scheduled' ? 'bg-apple-green text-white' : 'bg-gray-100 text-gray-500'}`}>
                          <Calendar className="w-5 h-5" />
                        </div>
                        <span className="font-bold text-apple-text text-lg">Schedule for Later</span>
                      </div>
                      <p className="text-sm text-apple-text-secondary pl-[52px]">Pick a specific date and time for the artisan to arrive.</p>
                    </button>
                  </motion.div>
                )}

                {/* Step 2: Details */}
                {step === 2 && (
                  <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-5">
                    <div>
                      <label className="block text-sm font-semibold text-apple-text mb-2">Service Details</label>
                      <textarea
                        required
                        rows={3}
                        value={details}
                        onChange={(e) => setDetails(e.target.value)}
                        placeholder="Describe what you need help with..."
                        className="w-full px-4 py-3 bg-gray-50 border-none rounded-2xl focus:ring-2 focus:ring-apple-green outline-none transition-shadow"
                      />
                    </div>

                    {bookingType === 'scheduled' && (
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-semibold text-apple-text mb-2">Date</label>
                          <div className="relative">
                            <Calendar className="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
                            <input type="date" required className="w-full pl-11 pr-4 py-3 bg-gray-50 border-none rounded-2xl focus:ring-2 focus:ring-apple-green outline-none transition-shadow text-apple-text font-medium" />
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-semibold text-apple-text mb-2">Time</label>
                          <div className="relative">
                            <Clock className="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
                            <input type="time" required className="w-full pl-11 pr-4 py-3 bg-gray-50 border-none rounded-2xl focus:ring-2 focus:ring-apple-green outline-none transition-shadow text-apple-text font-medium" />
                          </div>
                        </div>
                      </div>
                    )}

                    <div>
                      <label className="block text-sm font-semibold text-apple-text mb-2">Your Location</label>
                      <div className="relative">
                        <MapPin className="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
                        <input type="text" required defaultValue="Yaba, Lagos" className="w-full pl-11 pr-4 py-3 bg-gray-50 border-none rounded-2xl focus:ring-2 focus:ring-apple-green outline-none transition-shadow text-apple-text font-medium" />
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Step 3: Payment */}
                {step === 3 && (
                  <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-3">
                    <p className="text-sm font-semibold text-apple-text mb-3">Select Payment Method</p>

                    <label className={`flex items-center gap-4 p-4 border-2 rounded-2xl cursor-pointer transition-all active:scale-[0.98] ${paymentMethod === 'cash' ? 'border-apple-green bg-green-50/30' : 'border-gray-100 hover:border-gray-200'}`}>
                      <input type="radio" name="payment" checked={paymentMethod === 'cash'} onChange={() => setPaymentMethod('cash')} className="w-5 h-5 text-apple-green focus:ring-apple-green border-gray-300" />
                      <span className="font-bold text-apple-text">Cash on Delivery (Trackable)</span>
                    </label>
                    <label className={`flex items-center gap-4 p-4 border-2 rounded-2xl cursor-pointer transition-all active:scale-[0.98] ${paymentMethod === 'paystack' ? 'border-apple-green bg-green-50/30' : 'border-gray-100 hover:border-gray-200'}`}>
                      <input type="radio" name="payment" checked={paymentMethod === 'paystack'} onChange={() => setPaymentMethod('paystack')} className="w-5 h-5 text-apple-green focus:ring-apple-green border-gray-300" />
                      <span className="font-bold text-apple-text">Card/Transfer via Paystack</span>
                    </label>
                    <label className={`flex items-center gap-4 p-4 border-2 rounded-2xl cursor-pointer transition-all active:scale-[0.98] ${paymentMethod === 'flutterwave' ? 'border-apple-green bg-green-50/30' : 'border-gray-100 hover:border-gray-200'}`}>
                      <input type="radio" name="payment" checked={paymentMethod === 'flutterwave'} onChange={() => setPaymentMethod('flutterwave')} className="w-5 h-5 text-apple-green focus:ring-apple-green border-gray-300" />
                      <span className="font-bold text-apple-text">Card/Transfer via Flutterwave</span>
                    </label>
                  </motion.div>
                )}

                {/* Step 4: Tracking / Success */}
                {step === 4 && (
                  <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="flex flex-col items-center text-center py-6">
                    {bookingType === 'on-demand' ? (
                      <>
                        <div className="w-full h-48 bg-gray-100 rounded-3xl mb-8 relative overflow-hidden flex items-center justify-center border border-gray-200">
                          <MapIcon className="w-12 h-12 text-gray-300" />
                          <div className="absolute inset-0 bg-apple-blue/10 backdrop-blur-sm"></div>
                          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center">
                            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-lg mb-3">
                              <Navigation className="w-8 h-8 text-apple-blue" />
                            </div>
                            <span className="text-sm font-bold text-apple-blue bg-white/90 px-4 py-1.5 rounded-full shadow-sm backdrop-blur-md">Artisan is 1.2km away</span>
                          </div>
                        </div>
                        <h3 className="text-3xl font-bold text-apple-text mb-2 tracking-tight">Artisan is En Route!</h3>
                        <p className="text-apple-text-secondary mb-8 text-lg">{artisan.name} has accepted your request and is heading to your location.</p>
                      </>
                    ) : (
                      <>
                        <div className="w-20 h-20 bg-green-50 rounded-full flex items-center justify-center mb-8 mx-auto shadow-sm border border-green-100">
                          <AlertCircle className="w-10 h-10 text-apple-green" />
                        </div>
                        <h3 className="text-3xl font-bold text-apple-text mb-2 tracking-tight">Booking Scheduled!</h3>
                        <p className="text-apple-text-secondary mb-8 text-lg">Your appointment with {artisan.name} is confirmed.</p>
                      </>
                    )}
                    <Button onClick={resetAndClose} className="w-full" size="lg">Done</Button>
                  </motion.div>
                )}
              </div>

              {step !== 4 && (
                <div className="p-5 border-t bg-gray-50/50 flex justify-between rounded-b-3xl">
                  {step > 1 ? (
                    <Button type="button" variant="secondary" onClick={handleBack}>Back</Button>
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
