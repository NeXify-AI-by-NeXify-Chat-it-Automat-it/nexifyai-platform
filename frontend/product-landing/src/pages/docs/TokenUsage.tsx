import { ChevronRight, Info } from 'lucide-react';

export default function TokenUsage() {
  return (
    <div className="mx-auto flex max-w-6xl gap-8 px-4 py-12 sm:px-6 lg:px-8">
      <nav className="hidden w-56 shrink-0 lg:block">
        <div className="sticky top-24 space-y-1">
          {['how-tokens-work', 'cost-calculation', 'monitoring', 'best-practices'].map((id) => (
            <a key={id} href={`#${id}`} className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-[#9ca3af] hover:bg-white/5 hover:text-white">
              <ChevronRight className="h-3.5 w-3.5" />
              {id.split('-').map((w)=>w.charAt(0).toUpperCase()+w.slice(1)).join(' ')}
            </a>
          ))}
        </div>
      </nav>

      <div className="min-w-0 flex-1">
        <h1 className="text-3xl font-bold text-white">Token Usage &amp; Billing</h1>
        <p className="mt-2 text-[#9ca3af]">Understand how tokens are counted and billed.</p>

        <section id="how-tokens-work" className="mt-10">
          <h2 className="text-xl font-semibold text-white">How Tokens Work</h2>
          <p className="mt-2 text-sm text-[#9ca3af]">
            A token is a unit of text the model processes. ~0.75 words in English. Both input (prompt) and output (completion) tokens consume credits.
          </p>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <div className="rounded-lg border border-white/10 bg-surface-800 p-4">
              <h3 className="font-medium text-white">Input Tokens</h3>
              <p className="mt-1 text-sm text-[#9ca3af]">Your prompt messages, system instructions, conversation history. Billed at input rate.</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-surface-800 p-4">
              <h3 className="font-medium text-white">Output Tokens</h3>
              <p className="mt-1 text-sm text-[#9ca3af]">Model's generated response. Billed at output rate (typically higher).</p>
            </div>
          </div>
        </section>


        <section id="cost-calculation" className="mt-12">
          <h2 className="text-xl font-semibold text-white">Cost Calculation</h2>
          <div className="mt-4 rounded-lg border border-white/10 bg-surface-800 p-6">
            <p className="text-sm font-mono text-white">cost = (input_tokens × input_price_per_token) + (output_tokens × output_price_per_token)</p>
          </div>
          <div className="mt-4 overflow-x-auto rounded-lg border border-white/10">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-surface-800 text-left text-[#9ca3af]">
                  <th className="px-4 py-3 font-medium">Model</th>
                  <th className="px-4 py-3 font-medium text-right">Input / 1K</th>
                  <th className="px-4 py-3 font-medium text-right">Output / 1K</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {[
                  ['NeXify-Pro','€0.01440','€0.03520'],
                  ['NeXify-Flash','€0.00478','€0.00712'],
                  ['NeXify-Llama-70B','€0.00660','€0.01180'],
                  ['NeXify-Qwen-8B','€0.00530','€0.00790'],
                  ['NeXify-Qwen-14B','€0.00595','€0.00985'],
                  ['NeXify-Qwen-Coder-32B','€0.00725','€0.01440'],
                ].map((r)=>(
                  <tr key={r[0]} className="hover:bg-surface-800">
                    <td className="px-4 py-3 font-medium text-white">{r[0]}</td>
                    <td className="px-4 py-3 text-right text-gold-500">{r[1]}</td>
                    <td className="px-4 py-3 text-right text-gold-500">{r[2]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 flex items-start gap-2 rounded-lg bg-primary-500/10 p-4">
            <Info className="mt-0.5 h-4 w-4 shrink-0 text-primary-400" />
            <p className="text-sm text-[#9ca3af]">Prices per 1,000 tokens for readability. Full per-1M prices on Models &amp; Pricing page.</p>
          </div>
        </section>

        <section id="monitoring" className="mt-12">
          <h2 className="text-xl font-semibold text-white">Monitoring</h2>
          <p className="mt-2 text-sm text-[#9ca3af]">
            Track consumption from the <a href="/dashboard" className="text-primary-400 underline">Dashboard</a>. Every API response includes a <code className="rounded bg-surface-700 px-1.5 py-0.5 text-xs text-primary-300">usage</code> object.
          </p>
          <pre className="mt-4 overflow-x-auto rounded-lg border border-white/10 bg-[#0a0f14] p-4 text-sm text-[#dee3ed]">
{`{
  "usage": {
    "input_tokens": 145,
    "output_tokens": 32,
    "input_cost": 0.002088,
    "output_cost": 0.001126
  }
}`}
          </pre>
        </section>

        <section id="best-practices" className="mt-12">
          <h2 className="text-xl font-semibold text-white">Best Practices</h2>
          <ul className="mt-4 space-y-3">
            {[
              'Keep system prompts concise.',
              'Set temperature=0 for deterministic tasks.',
              'Set max_tokens to cap response length.',
              'Cache frequent responses client-side.',
              'Monitor dashboard daily.',
            ].map((tip,i)=>(
              <li key={i} className="flex items-start gap-3 text-sm text-[#9ca3af]">
                <span className="mt-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary-500/20 text-xs font-bold text-primary-400">{i+1}</span>
                {tip}
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}
