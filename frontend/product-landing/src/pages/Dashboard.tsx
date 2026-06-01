import { useState } from 'react';

export default function Dashboard() {
  const [apiKey, setApiKey] = useState('sk-nexify-xxxxxxxxxxxxxxxxxxxxx');

  const handleRegenerateKey = () => {
    setApiKey('sk-nexify-' + Math.random().toString(36).substring(2, 10));
  };

  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-white">Dashboard</h1>

      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border border-white/10 bg-surface-800 p-6">
          <p className="text-sm text-[#9ca3af]">Wallet Balance</p>
          <p className="mt-2 text-3xl font-bold text-white">€ 850.00</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-surface-800 p-6">
          <p className="text-sm text-[#9ca3af]">Total Requests</p>
          <p className="mt-2 text-3xl font-bold text-white">12,340</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-surface-800 p-6">
          <p className="text-sm text-[#9ca3af]">Total Tokens</p>
          <p className="mt-2 text-3xl font-bold text-white">1.2M</p>
        </div>
      </div>

      <div className="mt-10 rounded-lg border border-white/10 bg-surface-800 p-6">
        <h2 className="text-lg font-semibold text-white">API Key</h2>
        <div className="mt-2 flex items-center gap-3">
          <input
            readOnly
            value={apiKey}
            className="flex-1 rounded border border-white/10 bg-surface-700 px-3 py-2 text-sm text-[#dee3ed]"
          />
          <button
            onClick={handleRegenerateKey}
            className="rounded bg-primary-500 px-4 py-2 text-sm font-medium text-white hover:bg-primary-600"
          >
            Regenerate
          </button>
        </div>
        <p className="mt-2 text-xs text-[#6b7280]">
          Keep your API key secret. Regenerate immediately if exposed.
        </p>
      </div>

      <div className="mt-10 rounded-lg border border-white/10 bg-surface-800 p-6">
        <h2 className="text-lg font-semibold text-white">Recent Activity</h2>
        <table className="mt-4 w-full text-sm">
          <thead>
            <tr className="border-b border-white/10 text-left text-[#9ca3af]">
              <th className="pb-2 font-normal">Model</th>
              <th className="pb-2 font-normal">Requests</th>
              <th className="pb-2 font-normal">Tokens</th>
              <th className="pb-2 font-normal text-right">Cost</th>
            </tr>
          </thead>
          <tbody className="text-[#dee3ed]">
            {[['NeXify-Mega', 4500, '320K', '€48.00'], ['NeXify-Swift', 3200, '180K', '€22.50'], ['NeXify-Coder', 2100, '95K', '€14.25']].map(
              (row, i) => (
                <tr key={i} className="border-b border-white/5">
                  <td className="py-2">{row[0]}</td>
                  <td className="py-2">{row[1]}</td>
                  <td className="py-2">{row[2]}</td>
                  <td className="py-2 text-right text-gold-500">{row[3]}</td>
                </tr>
              ),
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
