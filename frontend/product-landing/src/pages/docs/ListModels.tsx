import { ChevronRight } from 'lucide-react';

const models = [
  { id: 'NeXify-Pro', context: 128000, type: 'chat' },
  { id: 'NeXify-Flash', context: 64000, type: 'chat' },
  { id: 'NeXify-Llama-70B', context: 128000, type: 'chat' },
  { id: 'NeXify-Qwen-8B', context: 32000, type: 'chat' },
  { id: 'NeXify-Qwen-14B', context: 64000, type: 'chat' },
  { id: 'NeXify-Qwen-Coder-32B', context: 128000, type: 'chat' },
];

export default function ListModels() {
  return (
    <div className="mx-auto flex max-w-6xl gap-8 px-4 py-12 sm:px-6 lg:px-8">
      <nav className="hidden w-56 shrink-0 lg:block">
        <div className="sticky top-24 space-y-1">
          {['overview','models','response'].map((id)=>(
            <a key={id} href={`#${id}`} className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-[#9ca3af] hover:bg-white/5 hover:text-white">
              <ChevronRight className="h-3.5 w-3.5" />
              {id.charAt(0).toUpperCase()+id.slice(1)}
            </a>
          ))}
        </div>
      </nav>

      <div className="min-w-0 flex-1">
        <h1 className="text-3xl font-bold text-white">List Models</h1>
        <p className="mt-2 text-[#9ca3af]">GET /v1/models — Lists all currently available models.</p>

        <section id="overview" className="mt-10">
          <div className="flex items-center gap-3">
            <span className="rounded bg-green-600 px-2 py-0.5 text-xs font-bold uppercase text-white">GET</span>
            <code className="text-sm text-white">https://api.nexifyai.cloud/v1/models</code>
          </div>
          <pre className="mt-4 overflow-x-auto rounded-lg border border-white/10 bg-[#0a0f14] p-4 text-sm text-[#dee3ed]">
{`curl https://api.nexifyai.cloud/v1/models \\
  -H "Authorization: Bearer sk-nexify-..."`}
          </pre>
        </section>

        <section id="models" className="mt-12">
          <h2 className="text-xl font-semibold text-white">Available Models</h2>
          <div className="mt-4 overflow-x-auto rounded-lg border border-white/10">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-surface-800 text-left text-[#9ca3af]">
                  <th className="px-4 py-3 font-medium">Model ID</th>
                  <th className="px-4 py-3 font-medium">Context Window</th>
                  <th className="px-4 py-3 font-medium">Type</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {models.map((m)=>(
                  <tr key={m.id} className="hover:bg-surface-800">
                    <td className="px-4 py-3 font-mono text-sm text-primary-300">{m.id}</td>
                    <td className="px-4 py-3 text-[#9ca3af]">{m.context.toLocaleString()} tokens</td>
                    <td className="px-4 py-3"><span className="rounded bg-surface-700 px-2 py-0.5 text-xs text-white">{m.type}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section id="response" className="mt-12">
          <h2 className="text-xl font-semibold text-white">Response</h2>
          <pre className="mt-4 overflow-x-auto rounded-lg border border-white/10 bg-[#0a0f14] p-4 text-sm text-[#dee3ed]">
{`{
  "object": "list",
  "data": [
    {
      "id": "NeXify-Pro",
      "object": "model",
      "context_window": 128000
    },
    ...
  ]
}`}
          </pre>
        </section>
      </div>
    </div>
  );
}
