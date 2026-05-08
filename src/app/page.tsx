import { Header } from '@/components/Header';
import { Button } from '@/components/Button';
import Link from 'next/link';
import { ArrowRight, ShieldCheck, Clock, MapPin, Search } from 'lucide-react';
import * as motion from 'framer-motion/client';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-apple-bg">
      <Header />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative pt-24 pb-32 overflow-hidden bg-apple-bg">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-apple-green/5 rounded-full blur-3xl -z-10 pointer-events-none"></div>

          <div className="container mx-auto px-4 text-center max-w-5xl relative z-10">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, ease: "easeOut" }}>
              <h1 className="text-6xl md:text-8xl font-bold text-apple-text tracking-tighter mb-6 leading-tight">
                Expert services. <br/>
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-apple-green to-apple-blue">On demand.</span>
              </h1>
              <p className="text-xl md:text-2xl text-apple-text-secondary mb-12 max-w-3xl mx-auto tracking-tight font-medium">
                Connect with verified local artisans instantly. From auto repair to custom tailoring, get premium service delivered to your location.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Link href="/login" className="w-full sm:w-auto">
                  <Button size="lg" className="w-full text-xl h-16 px-10 gap-2 shadow-[var(--shadow-apple-hover)] hover:scale-105 transition-transform duration-300 rounded-[24px]">
                    <Search className="w-6 h-6" />
                    Find an Artisan
                  </Button>
                </Link>
                <Link href="/login" className="w-full sm:w-auto">
                  <Button size="lg" variant="secondary" className="w-full text-xl h-16 px-10 rounded-[24px] bg-white border border-gray-200/50 hover:bg-gray-50 text-apple-text shadow-[var(--shadow-apple)] hover:scale-105 transition-transform duration-300">
                    Join as an Artisan
                  </Button>
                </Link>
              </div>

              <div className="mt-16 flex flex-wrap justify-center gap-x-10 gap-y-6 text-base font-semibold text-apple-text-secondary">
                <span className="flex items-center gap-2"><ShieldCheck className="w-5 h-5 text-apple-green" /> Verified Professionals</span>
                <span className="flex items-center gap-2"><Clock className="w-5 h-5 text-apple-green" /> Immediate Dispatch</span>
                <span className="flex items-center gap-2"><MapPin className="w-5 h-5 text-apple-green" /> Live Tracking</span>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-32 bg-white rounded-t-[48px] shadow-[0_-10px_40px_rgba(0,0,0,0.02)]">
          <div className="container mx-auto px-4 max-w-6xl">
            <div className="text-center mb-20">
              <h2 className="text-4xl md:text-5xl font-bold text-apple-text tracking-tight mb-4">Brilliantly simple.</h2>
              <p className="text-xl text-apple-text-secondary font-medium">How OgaArtisan connects you to quality.</p>
            </div>

            <div className="grid md:grid-cols-3 gap-12">
              <motion.div whileHover={{ y: -5 }} className="text-center">
                <div className="w-20 h-20 bg-gray-50 rounded-3xl flex items-center justify-center mx-auto mb-8 shadow-sm border border-gray-100">
                  <Search className="w-10 h-10 text-apple-text" />
                </div>
                <h3 className="text-2xl font-bold mb-3 tracking-tight">Discover</h3>
                <p className="text-apple-text-secondary text-lg leading-relaxed">Browse dozens of trades. Compare ratings, prices, and portfolios instantly.</p>
              </motion.div>
              <motion.div whileHover={{ y: -5 }} className="text-center">
                <div className="w-20 h-20 bg-gray-50 rounded-3xl flex items-center justify-center mx-auto mb-8 shadow-sm border border-gray-100">
                  <Clock className="w-10 h-10 text-apple-text" />
                </div>
                <h3 className="text-2xl font-bold mb-3 tracking-tight">Book</h3>
                <p className="text-apple-text-secondary text-lg leading-relaxed">Request immediate dispatch for emergencies, or schedule for later.</p>
              </motion.div>
              <motion.div whileHover={{ y: -5 }} className="text-center">
                <div className="w-20 h-20 bg-gray-50 rounded-3xl flex items-center justify-center mx-auto mb-8 shadow-sm border border-gray-100">
                  <MapPin className="w-10 h-10 text-apple-text" />
                </div>
                <h3 className="text-2xl font-bold mb-3 tracking-tight">Track</h3>
                <p className="text-apple-text-secondary text-lg leading-relaxed">Watch your artisan arrive in real-time. Pay securely via app or cash.</p>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Categories CTA */}
        <section className="py-32 bg-black text-white rounded-[48px] mx-4 md:mx-10 my-10 overflow-hidden relative">
          <div className="absolute inset-0 bg-gradient-to-br from-gray-900 to-black"></div>
          <div className="container mx-auto px-4 text-center max-w-4xl relative z-10">
            <h2 className="text-5xl md:text-7xl font-bold mb-8 tracking-tighter">30+ Categories.<br/>One app.</h2>
            <p className="text-gray-400 mb-12 text-xl md:text-2xl font-medium tracking-tight leading-relaxed">Whether you need a quick plumbing fix, a custom dress, or a full home renovation, our mobile network is ready.</p>
            <Link href="/user">
              <Button size="lg" className="bg-white !text-black hover:bg-gray-100 gap-2 h-16 px-10 text-xl rounded-full">
                Explore Categories <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
          </div>
        </section>
      </main>

      <footer className="bg-apple-bg py-12">
        <div className="container mx-auto px-4 text-center text-apple-text-secondary text-sm font-medium">
          <p>© {new Date().getFullYear()} OgaArtisan MVP. Designed for Africa.</p>
        </div>
      </footer>
    </div>
  );
}
