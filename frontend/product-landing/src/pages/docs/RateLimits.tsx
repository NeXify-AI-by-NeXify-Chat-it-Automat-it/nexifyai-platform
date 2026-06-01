import { ChevronRight } from 'lucide-react';

export default function RateLimits() {
  const plans = [
    { name: 'Free', requestsPerMinute: 60, tokensPerMinute: 50000 },
    { name: 'Pro', requestsPerMinute: 300, tokensPerMinute: 500000 },
    { name: 'Enterprise', requestsPerMinute: 1000, tokensPerMinute: 5000000 },
  ];

  return (
    <div className="mx-auto flex max-w-6xl gap-8 px-4 py-12 sm:px-6 lg:px-8">
      <nav className="hidden w-56 shrink-0 lg:block">
        <div className="sticky top-24 space-y-1">
          {['rate-limits'].map((id) => (
            <a key={id} href={`#${id}`} className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-[#9ca3af] hover:bg-white/5 hover:text-white">
              <ChevronRight className="h-3.5 w-3.5" />
              Rate Limits
            </a>
          ))}
        </div>
      </nav>

      <div className="min-w-0 flex-1">
        <h1 className="text-3xl font-bold text-white">Rate Limits</h1>
        <p className="mt-2 text-[#9ca3af]">Limits apply per API key and are enforced per minute.</p>
        <section id="rate-limits" className="mt-10">
          <div className="overflow-x-auto rounded-lg border border-white/10">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-surface-800 text-left text-[#9ca3af]">
                  <th className="px-4 py-3 font-medium">Plan</th>
                  <th className="px-4 py-3 font-medium">Requests / minute</th>
                  <th className="px-4 py-3 font-medium">Tokens / minute</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {plans.map((p) => (
                  <tr key={p.name} className="hover:bg-surface-800">
                    <td className="px-4 py-3 font-medium text-white">{p.name}</td>
                    <td className="px-4 py-3 text-[#9ca3af]">{p.requestsPerMinute}</td>
                    <td className="px-4 py-3 text-[#9ca3af]">{p.tokensPerMinute.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}
