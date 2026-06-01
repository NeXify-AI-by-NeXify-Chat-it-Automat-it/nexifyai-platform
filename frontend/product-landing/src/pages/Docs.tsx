export default function Docs() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-white">API Documentation</h1>
      <p className="mt-2 text-[#9ca3af]">The NeXify AI API uses a RESTful interface. All requests must include your API key in the Authorization header.</p>

      <section className="mt-10">
        <h2 className="text-xl font-semibold text-white">Authentication</h2>
        <p className="mt-2 text-sm text-[#9ca3af]">Include your API key as a Bearer token in the <code className="rounded bg-surface-700 px-1.5 py-0.5 text-primary-300">Authorization</code> header:</p>
        <pre className="mt-3 overflow-x-auto rounded-lg bg-surface-800 p-4 text-sm text-[#dee3ed]">
{`curl https://api.nexifyai.cloud/v1/chat/completions \\
  -H "Authorization: Bearer sk-nexify-..." \\
  -H "Content-Type: application/json" \\
  -d '{ ... }'`}
        </pre>
      </section>

      <section className="mt-10">
        <h2 className="text-xl font-semibold text-white">Endpoints</h2>
        <div className="mt-4 space-y-4">
          {[
            {
              method: 'POST',
              path: '/v1/chat/completions',
              desc: 'Generate a chat completion from a list of messages.',
            },
            {
              method: 'POST',
              path: '/v1/completions',
              desc: 'Generate a text completion from a prompt.',
            },
            {
              method: 'GET',
              path: '/v1/models',
              desc: 'List available models and their capabilities.',
            },
            {
              method: 'GET',
              path: '/v1/usage',
              desc: 'View current token usage and remaining balance.',
            },
          ].map((ep) => (
            <div key={ep.path} className="rounded-lg border border-white/10 bg-surface-800 p-4">
              <span className="inline-block rounded bg-surface-700 px-2 py-0.5 text-xs font-bold uppercase tracking-wide text-primary-400">
                {ep.method}
              </span>
              <code className="ml-2 text-sm text-white">{ep.path}</code>
              <p className="mt-2 text-sm text-[#9ca3af]">{ep.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-10">
        <h2 className="text-xl font-semibold text-white">Chat Completions Request</h2>
        <pre className="mt-3 overflow-x-auto rounded-lg bg-surface-800 p-4 text-sm text-[#dee3ed]">
{`{
  "model": "NeXify-Mega",
  "messages": [
    { "role": "system", "content": "You are a helpful assistant." },
    { "role": "user", "content": "What is the capital of France?" }
  ],
  "temperature": 0.7,
  "max_tokens": 1024
}`}
        </pre>
      </section>

      <section className="mt-10">
        <h2 className="text-xl font-semibold text-white">Response</h2>
        <pre className="mt-3 overflow-x-auto rounded-lg bg-surface-800 p-4 text-sm text-[#dee3ed]">
{`{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "model": "NeXify-Mega",
  "usage": {
    "input_tokens": 35,
    "output_tokens": 12,
    "input_cost": "0.15€",
    "output_cost": "0.18€"
  },
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris."
      },
      "finish_reason": "stop"
    }
  ]
}`}
        </pre>
      </section>

      <section className="mt-10">
        <h2 className="text-xl font-semibold text-white">Pricing</h2>
        <div className="mt-3 rounded-lg border border-gold-500/30 bg-surface-800 p-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-2 text-sm text-[#9ca3af]">
            <span>Input tokens</span>
            <span className="font-semibold text-gold-500">€9 / min</span>
          </div>
          <div className="flex items-center justify-between pt-2 text-sm text-[#9ca3af]">
            <span>Output tokens</span>
            <span className="font-semibold text-gold-500">€15 / min</span>
          </div>
          <p className="mt-3 text-xs text-[#6b7280]">
            Billed per minute of streaming usage. Unused minutes do not roll over.
          </p>
        </div>
      </section>

      <section className="mt-10">
        <h2 className="text-xl font-semibold text-white">SDKs</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-2">
          <div className="rounded-lg border border-white/10 bg-surface-800 p-4">
            <h3 className="font-medium text-white">Python</h3>
            <code className="mt-2 block text-sm text-[#9ca3af]">pip install nexify-ai</code>
            <p className="mt-2 text-xs text-[#6b7280]">Full async client with streaming support.</p>
          </div>
          <div className="rounded-lg border border-white/10 bg-surface-800 p-4">
            <h3 className="font-medium text-white">Node.js / TypeScript</h3>
            <code className="mt-2 block text-sm text-[#9ca3af]">npm install @nexifyai/sdk</code>
            <p className="mt-2 text-xs text-[#6b7280]">Native TypeScript types and auto-pagination.</p>
          </div>
        </div>
      </section>
    </div>
  );
}
