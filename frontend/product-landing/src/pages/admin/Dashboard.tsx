import { useEffect, useState } from 'react';
import { CreditCard, BarChart2, RefreshCw } from 'lucide-react';

interface Transaction {
  id: string;
  model: string;
  tokens: number;
  cost: number;
  date: string;
}

export default function AdminDashboard() {
  const [balance, setBalance] = useState<number>(0);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [usage, setUsage] = useState<{ inbound: number; outbound: number }>({ inbound: 0, outbound: 0 });

  // Load data – in real app replace with supabase calls
  useEffect(() => {
    // Mock balance
    setBalance(850);
    // Mock recent transactions
    setTransactions([
      { id: '1', model: 'NeXify-Pro', tokens: 3200, cost: 48, date: '2026-05-20' },
      { id: '2', model: 'NeXify-Qwen-8B', tokens: 1800, cost: 22.5, date: '2026-05-18' },
      { id: '3', model: 'NeXify-Flash', tokens: 950, cost: 14.25, date: '2026-05-15' },
    ]);
    // Mock usage chart data
    setUsage({ inbound: 120000, outbound: 85000 });
  }, []);

  const totalRequests = transactions.length;

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-white flex items-center gap-2">
        <CreditCard className="h-6 w-6 text-primary-400" /> Admin Dashboard
      </h1>

      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border border-white/10 bg-surface-800 p-6">
          <p className="text-sm text-[#9ca3af]">Wallet Balance</p>
          <p className="mt-2 text-3xl font-bold text-white">€ {balance.toFixed(2)}</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-surface-800 p-6">
          <p className="text-sm text-[#9ca3af]">Total Requests</p>
          <p className="mt-2 text-3xl font-bold text-white">{totalRequests}</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-surface-800 p-6">
          <p className="text-sm text-[#9ca3af]">Total Tokens</p>
          <p className="mt-2 text-3xl font-bold text-white">{(usage.inbound + usage.outbound).toLocaleString()}</p>
        </div>
      </div>

      <section className="mt-10">
        <h2 className="text-xl font-semibold text-white flex items-center gap-2">
          <BarChart2 className="h-5 w-5" /> API Usage (tokens)
        </h2>
        <div className="mt-4 h-40 w-full rounded bg-surface-700 p-4">
          {/* Simple bar chart simulation */}
          <div className="flex h-full items-end gap-2">
            <div className="flex-1 bg-primary-500" style={{ height: `${(usage.inbound / (usage.inbound + usage.outbound)) * 100}%` }} />
            <div className="flex-1 bg-gold-500" style={{ height: `${(usage.outbound / (usage.inbound + usage.outbound)) * 100}%` }} />
          </div>
          <div className="mt-2 flex justify-between text-sm text-[#9ca3af]">
            <span>Inbound</span>
            <span>Outbound</span>
          </div>
        </div>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 flex items-center gap-2 rounded bg-primary-500 px-4 py-2 text-sm font-medium text-white hover:bg-primary-600"
        >
          <RefreshCw className="h-4 w-4" /> Refresh
        </button>
      </section>

      <section className="mt-12">
        <h2 className="text-xl font-semibold text-white">Recent Activity</h2>
        <table className="mt-4 w-full text-sm">
          <thead>
            <tr className="border-b border-white/10 text-left text-[#9ca3af]">
              <th className="pb-2 font-normal">Model</th>
              <th className="pb-2 font-normal">Tokens</th>
              <th className="pb-2 font-normal">Cost (€)</th>
              <th className="pb-2 font-normal">Date</th>
            </tr>
          </thead>
          <tbody className="text-[#dee3ed]">
            {transactions.map((tx) => (
              <tr key={tx.id} className="border-b border-white/5">
                <td className="py-2">{tx.model}</td>
                <td className="py-2">{tx.tokens.toLocaleString()}</td>
                <td className="py-2 text-gold-500">{tx.cost.toFixed(2)}</td>
                <td className="py-2">{tx.date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
