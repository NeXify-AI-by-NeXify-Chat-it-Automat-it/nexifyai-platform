import { ChevronRight, Wallet } from 'lucide-react';

export default function GetBalance() {
  return (
    <div className="mx-auto flex max-w-6xl gap-8 px-4 py-12 sm:px-6 lg:px-8">
      <nav className="hidden w-56 shrink-0 lg:block">
        <div className="sticky top-24 space-y-1">
          {['overview','response','errors'].map((id)=>(
            <a key={id} href={`#${id}`} className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-[#9ca3af] hover:bg-white/5 hover:text-white">
              <ChevronRight className="h-3.5 w-3.5" />
              {id.charAt(0).toUpperCase()+id.slice(1)}
            </a>
          ))}
        </div>
      </nav>

      <div className="min-w-0 flex-1">
        <h1 className="text-3xl font-bold text-white">Get Balance</h1>
        <p className="mt-2 text-[#9ca3af]">GET /v1/user/balance — Returns your current prepaid wallet balance.</p>

        <section id="overview" className="mt-10">
          <div className="flex items-center gap-3">
            <span className="rounded bg-green-600 px-2 py-0.5 text-xs font-bold uppercase text-white">GET</span>
            <code className="text-sm text-white">https://api.nexifyai.cloud/v1/user/balance</code>
          </div>
          <pre className="mt-4 overflow-x-auto rounded-lg border border-white/10 bg-[#0a0f14] p-4 text-sm text-[#dee3ed]">
{`curl https://api.nexifyai.cloud/v1/user/balance \\
  -H "Authorization: Bearer sk-nexify-..."`}
          </pre>
        </section>

        <section id="response" className="mt-12">
          <h2 className="text-xl font-semibold text-white">Response</h2>
          <pre className="mt-4 overflow-x-auto rounded-lg border border-white/10 bg-[#0a0f14] p-4 text-sm text-[#dee3ed]">
{`{
  "object": "balance",
  "currency": "EUR",
  "balance": 850.00,
  "total_spent": 150.00,
  "last_top_up": "2026-05-20T10:30:00Z",
  "status": "active"
}`}
          </pre>
          <div className="mt-4 overflow-x-auto rounded-lg border border-white/10">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-surface-800 text-left text-[#9ca3af]">
                  <th className="px-4 py-3 font-medium">Field</th>
                  <th className="px-4 py-3 font-medium">Type</th>
                  <th className="px-4 py-3 font-medium">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {[
                  ['balance','number','Current prepaid credit in EUR.'],
                  ['total_spent','number','Total EUR spent across all time.'],
                  ['last_top_up','string (ISO 8601)','Timestamp of last top-up.'],
                  ['status','string','"active", "low_balance", or "empty".'],
                ].map((r)=>(
                  <tr key={r[0]} className="hover:bg-surface-800">
                    <td className="px-4 py-3 font-mono text-xs text-primary-300">{r[0]}</td>
                    <td className="px-4 py-3 text-white">{r[1]}</td>
                    <td className="px-4 py-3 text-[#9ca3af]">{r[2]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section id="errors" className="mt-12">
          <h2 className="text-xl font-semibold text-white">Errors</h2>
          <div className="mt-4 space-y-3">
            <div className="rounded-lg border border-white/10 bg-surface-800 p-4">
              <p className="font-mono text-sm text-primary-300">402 Insufficient Balance</p>
              <p className="mt-1 text-sm text-[#9ca3af]">Your wallet has zero credits. Top up via the Dashboard to resume service.</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-surface-800 p-4">
              <p className="font-mono text-sm text-primary-300">401 Unauthorized</p>
              <p className="mt-1 text-sm text-[#9ca3af]">Invalid or missing API key.</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
