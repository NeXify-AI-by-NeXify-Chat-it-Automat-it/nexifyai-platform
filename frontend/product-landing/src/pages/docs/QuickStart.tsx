import { useState } from 'react';
import { Copy, Check, ChevronRight } from 'lucide-react';

const tabs = ['curl', 'Python', 'Node.js'] as const;
type Tab = (typeof tabs)[number];

const codeExamples: Record<Tab, string> = {
  curl: `curl https://api.nexifyai.cloud/v1/chat/completions \\\n  -H "Authorization: Bearer sk-nexify-..." \\\n  -H "Content-Type: application/json" \\\n  -d '{\n    "model": "NeXify-Pro",\n    "messages": [\n      {"role": "user", "content": "Hello!"}\n    ]\n  }'`,
  Python: `import requests\n\nurl = "https://api.nexifyai.cloud/v1/chat/completions"\nheaders = {\n    "Authorization": "Bearer sk-nexify-...",\n    "Content-Type": "application/json"\n}\ndata = {\n    "model": "NeXify-Pro",\n    "messages": [{"role": "user", "content": "Hello!"}]\n}\n\nresponse = requests.post(url, headers=headers, json=data)\nprint(response.json())`,
  'Node.js': `const url = "https://api.nexifyai.cloud/v1/chat/completions";\n\nconst response = await fetch(url, {\n  method: "POST",\n  headers: {\n    "Authorization": "Bearer sk-nexify-...",\n    "Content-Type": "application/json",\n  },\n  body: JSON.stringify({\n    model: "NeXify-Pro",\n    messages: [{ role: "user", content: "Hello!" }],\n  }),\n});\n\nconst data = await response.json();\nconsole.log(data);`,
};


export default function QuickStart() {
  const [activeTab, setActiveTab] = useState<Tab>('curl');
  const [copied, setCopied] = useState(false);

  const copyCode = async () => {
    await navigator.clipboard.writeText(codeExamples[activeTab]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mx-auto flex max-w-6xl gap-8 px-4 py-12 sm:px-6 lg:px-8">
      {/* Sidebar */}
      <nav className="hidden w-56 shrink-0 lg:block">
        <div className="sticky top-24 space-y-1">
          {[
            { id: 'auth', label: 'Authentication' },
            { id: 'first-request', label: 'First Request' },
            { id: 'streaming', label: 'Streaming' },
            { id: 'next-steps', label: 'Next Steps' },
          ].map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-[#9ca3af] transition-colors hover:bg-white/5 hover:text-white"
            >
              <ChevronRight className="h-3.5 w-3.5" />
              {item.label}
            </a>
          ))}
        </div>
      </nav>

      {/* Content */}
      <div className="min-w-0 flex-1">
        <h1 className="text-3xl font-bold text-white">Quick Start</h1>
        <p className="mt-2 text-[#9ca3af]">Get up and running with NeXify AI in under 5 minutes.</p>

        <section id="auth" className="mt-10">
          <h2 className="text-xl font-semibold text-white">1. Get Your API Key</h2>
          <p className="mt-2 text-sm text-[#9ca3af]">
            Sign in to the <a href="/dashboard" className="text-primary-400 underline">NeXify Dashboard</a> and generate an API key.
          </p>
          <div className="mt-4 rounded-lg border border-white/10 bg-surface-800 p-4">
            <p className="text-sm text-[#9ca3af]"><span className="font-semibold text-gold-500">Important:</span> Keep key secret.</p>
          </div>
        </section>

        <section id="first-request" className="mt-12">
          <h2 className="text-xl font-semibold text-white">2. Make Your First Request</h2>
          <p className="mt-2 text-sm text-[#9ca3af]">All requests go to <code className="rounded bg-surface-700 px-1.5 py-0.5 text-xs text-primary-300">https://api.nexifyai.cloud/v1</code>.</p>

          <div className="mt-4 flex gap-1 rounded-lg bg-surface-800 p-1">
            {tabs.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`rounded-md px-4 py-2 text-sm font-medium ${activeTab===tab?'bg-primary-500 text-white':'text-[#9ca3af] hover:text-white'}`}
              >{tab}</button>
            ))}
          </div>

          <div className="relative mt-2">
            <pre className="overflow-x-auto rounded-lg border border-white/10 bg-[#0a0f14] p-4 text-sm text-[#dee3ed]"><code>{codeExamples[activeTab]}</code></pre>
            <button onClick={copyCode} className="absolute right-3 top-3 rounded-md bg-white/10 p-2 text-[#9ca3af] hover:bg-white/20 hover:text-white">
              {copied ? <Check className="h-4 w-4 text-green-400"/> : <Copy className="h-4 w-4"/>}
            </button>
          </div>
        </section>

        <section id="streaming" className="mt-12">
          <h2 className="text-xl font-semibold text-white">3. Streaming</h2>
          <p className="mt-2 text-sm text-[#9ca3af]">Add <code className="rounded bg-surface-700 px-1.5 py-0.5 text-xs text-primary-300">stream: true</code> to receive SSE.</p>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <div className="rounded-lg border border-white/10 bg-surface-800 p-4">
              <h3 className="font-medium text-white">Python</h3>
              <pre className="text-sm text-[#dee3ed]">{`import requests\n\nurl = "https://api.nexifyai.cloud/v1/chat/completions"\nheaders = {"Authorization": "Bearer sk-nexify-..."}\ndata = {\n  "model": "NeXify-Pro",\n  "stream": True,\n  "messages": [{"role": "user", "content": "Hi"}]\n}\n\nwith requests.post(url, headers=headers, json=data, stream=True) as r:\n  for line in r.iter_lines():\n    if line:\n      print(line.decode())`}</pre>
            </div>
            <div className="rounded-lg border border-white/10 bg-surface-800 p-4">
              <h3 className="font-medium text-white">Node.js</h3>
              <pre className="text-sm text-[#dee3ed]">{`const response = await fetch("https://api.nexifyai.cloud/v1/chat/completions", {\n  method: "POST",\n  headers: {\n    "Authorization": "Bearer sk-nexify-...",\n    "Content-Type": "application/json"\n  },\n  body: JSON.stringify({\n    model: "NeXify-Pro",\n    stream: true,\n    messages: [{ role: "user", content: "Hi" }]\n  })\n});\n\nconst reader = response.body.getReader();\nconst decoder = new TextDecoder();\nwhile (true) {\n  const {done, value} = await reader.read();\n  if (done) break;\n  console.log(decoder.decode(value));\n}`}</pre>
            </div>
          </div>
        </section>

        <section id="next-steps" className="mt-12">
          <h2 className="text-xl font-semibold text-white">4. Next Steps</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            {[
              {title:'Available Models',href:'/docs#models',desc:'See all models.'},
              {title:'Pricing',href:'/docs#pricing',desc:'Token costs.'},
              {title:'API Reference',href:'/docs#create-chat-completion',desc:'Full parameters.'},
            ].map(item=> (
              <a key={item.title} href={item.href} className="rounded-lg border border-white/10 bg-surface-800 p-4 hover:border-primary-500/30">
                <h3 className="font-medium text-white">{item.title}</h3>
                <p className="mt-1 text-sm text-[#9ca3af]">{item.desc}</p>
              </a>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
