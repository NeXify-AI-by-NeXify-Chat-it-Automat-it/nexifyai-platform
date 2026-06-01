import { ChevronRight } from 'lucide-react';

interface ModelInfo {
  name: string;
  providerBase: string;
  context: string;
  inputPrice: string;
  outputPrice: string;
}

const MODELS: ModelInfo[] = [
  { name: 'NeXify-Pro', providerBase: 'NeXify-v4-pro', context: '128K', inputPrice: '€14.40', outputPrice: '€35.20' },
  { name: 'NeXify-Flash', providerBase: 'NeXify-v4-flash', context: '64K', inputPrice: '€4.78', outputPrice: '€7.12' },
  { name: 'NeXify-Llama-70B', providerBase: 'meta-llama/Llama-3.3-70B', context: '128K', inputPrice: '€6.60', outputPrice: '€11.80' },
];

const FAQ = [
  { q: 'How is pricing calculated?', a: 'Every model price = (provider base price × 1.30) + €4.00 markup per 1M tokens. Covers infrastructure, API gateway, and support.' },
  { q: 'Do unused tokens roll over?', a: 'Credits are prepaid and do not expire. Tokens deducted in real-time from wallet balance.' },
  { q: 'Volume discounts?', a: 'Contact sales@nexifyai.cloud for enterprise pricing above 100M tokens/month.' },
];

export default function ModelsAndPricing() {
  return (
    <div className="mx-auto flex max-w-6xl gap-8 px-4 py-12 sm:px-6 lg:px-8">
      <nav className="hidden w-56 shrink-0 lg:block">
        <div className="sticky top-24 space-y-1">
          {['models-table', 'pricing-formula', 'faq'].map((id) => (
            <a key={id} href={`#${id}`} className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-[#9ca3af] hover:bg-white/5 hover:text-white">
              <ChevronRight className="h-3.5 w-3.5" />
              {id === 'models-table' ? 'Models' : id === 'pricing-formula' ? 'Pricing Formula' : 'FAQ'}
            </a>
          ))}
        </div>
      </nav>

      <div className="min-w-0 flex-1">
        <h1 className="text-3xl font-bold text-white">Models &amp; Pricing</h1>
        <p className="mt-2 text-[#9ca3af]">All NeXify models with per-1M-token pricing. Prepaid credits only.</p>

        <section id="models-table" className="mt-10">
          <h2 className="text-xl font-semibold text-white">Available Models</h2>
          <div className="mt-4 overflow-x-auto rounded-lg border border-white/10">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10 bg-surface-800 text-left text-[#9ca3af]">
                  <th className="px-4 py-3 font-medium">Model</th>
                  <th className="px-4 py-3 font-medium">Provider Base</th>
                  <th className="px-4 py-3 font-medium">Context</th>
                  <th className="px-4 py-3 font-medium text-right">Input/1M</th>
                  <th className="px-4 py-3 font-medium text-right">Output/1M</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {MODELS.map((m) => (
                  <tr key={m.name} className="transition-colors hover:bg-surface-800">
                    <td className="px-4 py-3 font-medium text-white">{m.name}</td>
                    <td className="px-4 py-3 text-[#9ca3af]">{m.providerBase}</td>
                    <td className="px-4 py-3 text-[#9ca3af]">{m.context}</td>
                    <td className="px-4 py-3 text-right font-semibold text-gold-500">{m.inputPrice}</td>
                    <td className="px-4 py-3 text-right font-semibold text-gold-500">{m.outputPrice}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section id="pricing-formula" className="mt-12">
          <h2 className="text-xl font-semibold text-white">Pricing Formula</h2>
          <div className="mt-4 rounded-lg border border-gold-500/30 bg-surface-800 p-6">
            <p className="text-lg font-mono text-white">Final Price = (Provider Base × 1.30) + €4.00 per 1M tokens</p>
            <p className="mt-3 text-sm text-[#9ca3af]">Example: Base €8.00 → (8.00 × 1.30) + 4.00 = €14.40 / 1M input tokens.</p>
          </div>
          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            {[
              { label: 'Provider rate multiplier', val: '×1.30' },
              { label: 'Infrastructure fee', val: '€4.00/1M tokens' },
              { label: 'Billing model', val: 'Prepaid credits' },
            ].map((item) => (
              <div key={item.label} className="rounded-lg border border-white/10 bg-surface-800 p-4">
                <p className="text-sm text-[#9ca3af]">{item.label}</p>
                <p className="mt-1 text-lg font-bold text-white">{item.val}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="faq" className="mt-12">
          <h2 className="text-xl font-semibold text-white">FAQ</h2>
          <div className="mt-4 space-y-3">
            {FAQ.map((item) => (
              <details key={item.q} className="group rounded-lg border border-white/10 bg-surface-800">
                <summary className="flex cursor-pointer items-center justify-between px-4 py-3 text-sm font-medium text-white">
                  {item.q}
                  <ChevronRight className="h-4 w-4 transition-transform group-open:rotate-90" />
                </summary>
                <p className="border-t border-white/10 px-4 py-3 text-sm text-[#9ca3af]">{item.a}</p>
              </details>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}


