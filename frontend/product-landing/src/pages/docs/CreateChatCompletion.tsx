import { ChevronRight } from 'lucide-react';

export default function CreateChatCompletion() {
  return (
    <div className="mx-auto flex max-w-6xl gap-8 px-4 py-12 sm:px-6 lg:px-8">
      <nav className="hidden w-56 shrink-0 lg:block">
        <div className="sticky top-24 space-y-1">
          {['overview','request','response','streaming'].map((id)=>(
            <a key={id} href={`#${id}`} className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-[#9ca3af] hover:bg-white/5 hover:text-white">
              <ChevronRight className="h-3.5 w-3.5" />
              {id.charAt(0).toUpperCase()+id.slice(1)}
            </a>
          ))}
        </div>
      </nav>

      <div className="min-w-0 flex-1">
        <h1 className="text-3xl font-bold text-white">Create Chat Completion</h1>
        <p className="mt-2 text-[#9ca3af]">POST /v1/chat/completions — Generate a model response for a chat conversation.</p>

        <section id="overview" className="mt-10">
          <div className="flex items-center gap-3">
            <span className="rounded bg-primary-500 px-2 py-0.5 text-xs font-bold uppercase text-white">POST</span>
            <code className="text-sm text-white">https://api.nexifyai.cloud/v1/chat/completions</code>
          </div>
        </section>

        <section id="request" className="mt-10">
          <h2 className="text-xl font-semibold text-white">Request Body</h2>
          <div className="mt-4 overflow-x-auto rounded-lg border border-white/10">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-surface-800 text-left text-[#9ca3af]">
                  <th className="px-4 py-3 font-medium">Parameter</th>
                  <th className="px-4 py-3 font-medium">Type</th>
                  <th className="px-4 py-3 font-medium">Required</th>
                  <th className="px-4 py-3 font-medium">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {[
                  ['model','string','Yes','Model ID, e.g. NeXify-Pro.'],
                  ['messages','array','Yes','Array of message objects with role and content.'],
                  ['temperature','number','No','Sampling temperature 0-2. Default 0.7.'],
                  ['max_tokens','integer','No','Maximum output tokens. Default varies by model.'],
                  ['stream','boolean','No','If true, returns SSE stream. Default false.'],
                  ['top_p','number','No','Nucleus sampling. Default 1.'],
                ].map((r)=>(
                  <tr key={r[0]} className="hover:bg-surface-800">
                    <td className="px-4 py-3 font-mono text-xs text-primary-300">{r[0]}</td>
                    <td className="px-4 py-3 text-white">{r[1]}</td>
                    <td className="px-4 py-3 text-white">{r[2]}</td>
                    <td className="px-4 py-3 text-[#9ca3af]">{r[3]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <pre className="mt-4 overflow-x-auto rounded-lg border border-white/10 bg-[#0a0f14] p-4 text-sm text-[#dee3ed]">
{`{
  "model": "NeXify-Pro",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing."}
  ],
  "temperature": 0.7,
  "max_tokens": 512,
  "stream": false
}`}
          </pre>
        </section>

        <section id="response" className="mt-12">
          <h2 className="text-xl font-semibold text-white">Response</h2>
          <pre className="mt-4 overflow-x-auto rounded-lg border border-white/10 bg-[#0a0f14] p-4 text-sm text-[#dee3ed]">
{`{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "model": "NeXify-Pro",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Quantum computing uses qubits..."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "input_tokens": 42,
    "output_tokens": 156
  }
}`}
          </pre>
        </section>

        <section id="streaming" className="mt-12">
          <h2 className="text-xl font-semibold text-white">Streaming (SSE)</h2>
          <p className="mt-2 text-sm text-[#9ca3af]">When stream:true, chunks arrive as data: [JSON]\n\n.</p>
          <pre className="mt-4 overflow-x-auto rounded-lg border border-white/10 bg-[#0a0f14] p-4 text-sm text-[#dee3ed]">
{`data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","choices":[{"delta":{"content":"Quantum"}}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","choices":[{"delta":{"content":" computing"}}]}

data: [DONE]`}
          </pre>
        </section>
      </div>
    </div>
  );
}
