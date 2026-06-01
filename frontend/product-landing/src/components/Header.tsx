import { Link } from 'react-router-dom';

export default function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-surface-900/80 backdrop-blur">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8">
            <Link to="/" className="text-2xl font-bold text-white tracking-tight">
              NeX<span className="text-primary-500">ify</span> AI
            </Link>
            <nav className="hidden md:flex items-center gap-6">
              <Link to="/models" className="text-sm text-[#dee3ed] hover:text-white transition-colors">
                Models
              </Link>
              <Link to="/docs" className="text-sm text-[#dee3ed] hover:text-white transition-colors">
                Documentation
              </Link>
              <Link to="/dashboard" className="text-sm text-[#dee3ed] hover:text-white transition-colors">
                Dashboard
              </Link>
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="rounded-lg px-4 py-2 text-sm font-medium text-[#dee3ed] hover:text-white hover:bg-white/5 transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="rounded-lg bg-primary-500 px-4 py-2 text-sm font-medium text-white hover:bg-primary-600 transition-colors"
            >
              Get Started
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
