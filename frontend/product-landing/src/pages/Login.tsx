import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Placeholder: integrate Supabase auth here
    console.log('Login', { email, password });
    navigate('/dashboard');
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-900">
      <div className="w-full max-w-md rounded-lg bg-surface-800 p-8 shadow-lg">
        <h2 className="mb-6 text-center text-2xl font-bold text-white">Sign In</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded border border-white/10 bg-surface-700 px-3 py-2 text-[#dee3ed] placeholder-[#9ca3af] focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded border border-white/10 bg-surface-700 px-3 py-2 text-[#dee3ed] placeholder-[#9ca3af] focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
          <button
            type="submit"
            className="w-full rounded bg-primary-500 py-2 font-medium text-white hover:bg-primary-600"
          >
            Sign In
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-[#9ca3af]">
          Don\'t have an account?{' '}
          <Link to="/register" className="text-primary-400 hover:underline">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
