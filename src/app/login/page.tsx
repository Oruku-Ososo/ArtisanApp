'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Mail, ArrowRight, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/Button';
import Link from 'next/link';

export default function Login() {
  const [email, setEmail] = useState('');
  const [role, setRole] = useState<'user' | 'artisan'>('user');
  const [step, setStep] = useState<'email' | 'otp'>('email');
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  const handleSendOtp = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setIsSubmitting(true);
    // Simulate sending OTP
    setTimeout(() => {
      setIsSubmitting(false);
      setStep('otp');
    }, 1000);
  };

  const handleVerifyOtp = (e: React.FormEvent) => {
    e.preventDefault();
    const otpValue = otp.join('');
    if (otpValue.length !== 6) return;

    setIsSubmitting(true);
    // Simulate OTP verification and login
    setTimeout(() => {
      setIsSubmitting(false);
      if (role === 'user') {
        router.push('/user');
      } else {
        router.push('/artisan');
      }
    }, 1000);
  };

  const handleOtpChange = (index: number, value: string) => {
    if (value.length > 1) return;
    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto focus next input
    if (value && index < 5) {
      const nextInput = document.getElementById(`otp-${index + 1}`);
      nextInput?.focus();
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <Link href="/" className="flex justify-center items-center gap-2 mb-6">
          <span className="w-8 h-8 bg-green-600 text-white flex items-center justify-center rounded-md font-bold text-xl">O</span>
          <span className="text-2xl font-bold text-green-700 tracking-tight">OgaArtisan</span>
        </Link>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          {step === 'email' ? 'Sign in to your account' : 'Verify your email'}
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          {step === 'email' ? 'Use your email to receive a secure login code.' : `We sent a 6-digit code to ${email}`}
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-xl sm:px-10 border border-gray-100">

          {step === 'email' ? (
            <form className="space-y-6" onSubmit={handleSendOtp}>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">I am logging in as a...</label>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    type="button"
                    onClick={() => setRole('user')}
                    className={`py-3 px-4 rounded-lg border-2 flex items-center justify-center gap-2 transition-colors ${role === 'user' ? 'border-green-600 bg-green-50 text-green-800' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}
                  >
                    {role === 'user' && <CheckCircle2 className="w-4 h-4 text-green-600" />}
                    Customer
                  </button>
                  <button
                    type="button"
                    onClick={() => setRole('artisan')}
                    className={`py-3 px-4 rounded-lg border-2 flex items-center justify-center gap-2 transition-colors ${role === 'artisan' ? 'border-green-600 bg-green-50 text-green-800' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}
                  >
                    {role === 'artisan' && <CheckCircle2 className="w-4 h-4 text-green-600" />}
                    Artisan
                  </button>
                </div>
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email address
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 sm:text-sm transition-shadow"
                    placeholder="you@example.com"
                  />
                </div>
              </div>

              <Button type="submit" fullWidth size="lg" disabled={isSubmitting || !email}>
                {isSubmitting ? 'Sending...' : 'Send Login Code'}
              </Button>
            </form>
          ) : (
            <form className="space-y-6" onSubmit={handleVerifyOtp}>
              <div>
                <label className="block text-sm font-medium text-gray-700 text-center mb-4">
                  Enter the 6-digit code
                </label>
                <div className="flex justify-center gap-2 sm:gap-3">
                  {otp.map((digit, index) => (
                    <input
                      key={index}
                      id={`otp-${index}`}
                      type="text"
                      inputMode="numeric"
                      pattern="[0-9]*"
                      maxLength={1}
                      value={digit}
                      onChange={(e) => handleOtpChange(index, e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Backspace' && !digit && index > 0) {
                          const prevInput = document.getElementById(`otp-${index - 1}`);
                          prevInput?.focus();
                        }
                      }}
                      className="w-10 h-12 sm:w-12 sm:h-14 text-center text-xl font-bold border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    />
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between mt-4">
                <button
                  type="button"
                  onClick={() => setStep('email')}
                  className="text-sm text-green-600 hover:text-green-500 font-medium"
                >
                  Change email
                </button>
                <button
                  type="button"
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  Resend code
                </button>
              </div>

              <Button type="submit" fullWidth size="lg" disabled={isSubmitting || otp.join('').length !== 6}>
                {isSubmitting ? 'Verifying...' : 'Verify & Login'} <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
