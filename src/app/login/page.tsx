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
    <div className="min-h-screen bg-apple-bg flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Decorative background blur */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-lg h-[400px] bg-apple-blue/10 rounded-full blur-[100px] -z-10 pointer-events-none"></div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <Link href="/" className="flex justify-center items-center gap-2 mb-8">
          <span className="w-10 h-10 bg-apple-text text-white flex items-center justify-center rounded-xl font-bold text-2xl shadow-sm">O</span>
        </Link>
        <h2 className="mt-2 text-center text-3xl md:text-4xl font-bold text-apple-text tracking-tight">
          {step === 'email' ? 'Sign in' : 'Verify email'}
        </h2>
        <p className="mt-3 text-center text-base text-apple-text-secondary font-medium">
          {step === 'email' ? 'Use your email to securely sign in or create an account.' : `Enter the 6-digit code sent to ${email}`}
        </p>
      </div>

      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-[420px]">
        <div className="glass-card py-10 px-6 sm:rounded-[32px] sm:px-10 shadow-[var(--shadow-apple)] border border-gray-100/50">

          {step === 'email' ? (
            <form className="space-y-6" onSubmit={handleSendOtp}>
              <div>
                <label className="block text-sm font-semibold text-apple-text mb-3">Account Type</label>
                <div className="flex p-1 bg-gray-100/80 rounded-2xl">
                  <button
                    type="button"
                    onClick={() => setRole('user')}
                    className={`flex-1 py-2.5 px-4 rounded-xl text-sm font-semibold transition-all ${role === 'user' ? 'bg-white text-apple-text shadow-sm' : 'text-gray-500 hover:text-gray-900'}`}
                  >
                    Customer
                  </button>
                  <button
                    type="button"
                    onClick={() => setRole('artisan')}
                    className={`flex-1 py-2.5 px-4 rounded-xl text-sm font-semibold transition-all ${role === 'artisan' ? 'bg-white text-apple-text shadow-sm' : 'text-gray-500 hover:text-gray-900'}`}
                  >
                    Artisan
                  </button>
                </div>
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-semibold text-apple-text mb-2">
                  Email address
                </label>
                <div className="mt-1 relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
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
                    className="block w-full pl-11 pr-4 py-3.5 bg-gray-50 border-none rounded-2xl focus:ring-2 focus:ring-apple-blue transition-shadow text-apple-text font-medium outline-none"
                    placeholder="name@example.com"
                  />
                </div>
              </div>

              <Button type="submit" fullWidth size="lg" disabled={isSubmitting || !email} className="mt-8 text-[17px]">
                {isSubmitting ? 'Sending code...' : 'Continue with Email'}
              </Button>
            </form>
          ) : (
            <form className="space-y-8" onSubmit={handleVerifyOtp}>
              <div>
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
                      className="w-12 h-14 sm:w-14 sm:h-16 text-center text-2xl font-bold bg-gray-50 border-none rounded-2xl focus:ring-2 focus:ring-apple-blue outline-none transition-shadow text-apple-text"
                    />
                  ))}
                </div>
              </div>

              <div className="flex flex-col gap-4 text-center">
                <Button type="submit" fullWidth size="lg" disabled={isSubmitting || otp.join('').length !== 6} className="text-[17px]">
                  {isSubmitting ? 'Verifying...' : 'Verify'} <ArrowRight className="w-5 h-5 ml-2" />
                </Button>

                <div className="flex items-center justify-center gap-4 text-sm font-medium mt-2">
                  <button
                    type="button"
                    onClick={() => setStep('email')}
                    className="text-apple-blue hover:text-apple-blue-hover transition-colors"
                  >
                    Change email
                  </button>
                  <span className="text-gray-300">|</span>
                  <button
                    type="button"
                    className="text-gray-500 hover:text-gray-800 transition-colors"
                  >
                    Resend code
                  </button>
                </div>
              </div>
            </form>
          )}
        </div>

        <p className="text-center text-sm text-apple-text-secondary mt-8 font-medium">
          By continuing, you agree to our Terms of Service and Privacy Policy.
        </p>
      </div>
    </div>
  );
}
