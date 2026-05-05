import { Header } from '@/components/Header';
import { Button } from '@/components/Button';
import Link from 'next/link';
import { ArrowRight, ShieldCheck, Clock, MapPin, Search } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Header />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative pt-20 pb-32 overflow-hidden bg-white">
          <div className="absolute inset-0 bg-green-50/50 -z-10"></div>
          <div className="container mx-auto px-4 text-center max-w-4xl relative z-10">
            <h1 className="text-5xl md:text-6xl font-extrabold text-gray-900 tracking-tight mb-6">
              Find Expert <span className="text-green-600">Local Artisans</span> On-Demand
            </h1>
            <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
              From auto mechanics to tailors, plumbers to beauticians. Connect with verified professionals near you for immediate service or schedule for later.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="/login">
                <Button size="lg" className="gap-2 px-8 py-6 text-lg rounded-xl w-full sm:w-auto shadow-lg shadow-green-200">
                  <Search className="w-5 h-5" />
                  Find an Artisan Now
                </Button>
              </Link>
              <Link href="/login">
                <Button size="lg" variant="outline" className="px-8 py-6 text-lg rounded-xl w-full sm:w-auto bg-white">
                  Join as an Artisan
                </Button>
              </Link>
            </div>

            <div className="mt-12 flex flex-wrap justify-center gap-x-8 gap-y-4 text-sm font-medium text-gray-500">
              <span className="flex items-center gap-1.5"><ShieldCheck className="w-4 h-4 text-green-500" /> Verified Professionals</span>
              <span className="flex items-center gap-1.5"><Clock className="w-4 h-4 text-green-500" /> On-Demand Service</span>
              <span className="flex items-center gap-1.5"><MapPin className="w-4 h-4 text-green-500" /> Track in Real-Time</span>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-24 bg-white border-t border-gray-100">
          <div className="container mx-auto px-4 max-w-6xl">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">How OgaArtisan Works</h2>
              <p className="text-lg text-gray-600">The easiest way to get things fixed, built, or tailored in Nigeria.</p>
            </div>

            <div className="grid md:grid-cols-3 gap-12">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-sm">
                  <Search className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-semibold mb-3">1. Find Your Artisan</h3>
                <p className="text-gray-600">Browse through dozens of categories from construction to personal care. See ratings and prices instantly.</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-green-100 text-green-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-sm">
                  <Clock className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-semibold mb-3">2. Book On-Demand</h3>
                <p className="text-gray-600">Need it now? Book an available artisan for immediate dispatch. Or schedule for a later time.</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-purple-100 text-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-sm">
                  <MapPin className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-semibold mb-3">3. Track & Pay</h3>
                <p className="text-gray-600">Track your artisan&apos;s location in real-time. Pay securely via card, transfer, or cash on delivery.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Categories CTA */}
        <section className="py-20 bg-gray-900 text-white">
          <div className="container mx-auto px-4 text-center max-w-3xl">
            <h2 className="text-3xl font-bold mb-6">Over 30+ Trade Categories</h2>
            <p className="text-gray-400 mb-10 text-lg">Whether you need a quick plumbing fix, a custom dress, or a full home renovation, our mobile network of artisans is ready to serve you anywhere in Nigeria.</p>
            <Link href="/user">
              <Button size="lg" className="bg-white text-gray-900 hover:bg-gray-100 gap-2">
                Explore Categories <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </section>
      </main>

      <footer className="bg-white border-t py-10">
        <div className="container mx-auto px-4 text-center text-gray-500 text-sm">
          <p>© {new Date().getFullYear()} OgaArtisan MVP. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
