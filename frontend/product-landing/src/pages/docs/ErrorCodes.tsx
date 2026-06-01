import { ChevronRight } from 'lucide-react';

const errors = [
  { code: 400, name: 'Bad Request', description: 'Invalid request body or parameters.' },
  { code: 401, name: 'Unauthorized', description: 'Missing, invalid, or expired API key.' },
  { code: 402, name: 'Insufficient Balance', description: 'Your prepaid wallet has zero credits. Top up to continue.' },
  { code: 404, name: 'Not Found', description: 'The requested endpoint or model does not exist.' },
  { code: 429, name: 'Rate Limited', description: 'Too many requests. Retry after the indicated time.' },
  { code: 500, name: 'Internal Server Error', description: 'Something went wrong on our side. Retry with exponential backoff.' },
  { code: 503, name: 'Service Unavailable', description: 'Temporary overload or maintenance. Check status.nexifyai.cloud.' },
];

export default function ErrorCodes() {
  return (
    <div className="mx-auto flex max-w-6xl gap-8 px-4 py-12 sm:px-6 lg:px-8">
      <nav className="hidden w-56 shrink-0 lg:block">
        <div className="sticky top-24 space-y-1">
          {['error-table', 'retry-logic'].map((id) => (
            <a key={id} href={`#${id}`} className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-[#9ca3af] hover:bg-white/5 hover:text-white">
              <ChevronRight className="h-3.5 w-3.5" />
              {id.split('-').map((w)=>w.charAt(0).toUpperCase()+w.slice(1)).join(' ')}
            </a>
          ))}
        </div>
      </nav>

      <div className="min-w-0 flex-1">
        <h1 className="text-3xl font-bold text-white">Error Codes</h1>
        <p className="mt-2 text-[#9ca3af]">HTTP status codes returned by the NeXify API.</p>

        <section id="error-table" className="mt-10">
          <div className="overflow-x-auto rounded-lg border border-white/10">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-surface-800 text-left text-[#9ca3af]">
                  <th className="px-4 py-3 font-medium">Code</th>
                  <th className="px-4 py-3 font-medium">Name</th>
                  <th className="px-4 py-3 font-medium">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {errors.map((e) => (
                  <tr key={e.code} className="hover:bg-surface-800">
                    <td className="px-4 py-3">
                      <span className="rounded-md bg-surface-700 px-2 py-1 font-mono text-xs text-white">{e.code}</span>
                    </td>
                    <td className="px-4 py-3 font-medium text-white">{e.name}</td>
                    <td className="px-4 py-3 text-[#9ca3af]">{e.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section id="retry-logic" className="mt-12">
          <h2 className="text-xl font-semibold text-white">Retry Logic</h2>
          <p className="mt-2 text-sm text-[#9ca3af]">
            Implement exponential backoff for 429 and 5xx errors. Start with 1s delay, double each retry, max 5 retries.
          </p>
          <pre className="mt-4 overflow-x-auto rounded-lg border border-white/10 bg-[#0a0f14] p-4 text-sm text-[#dee3ed]">
{`// Python example
import time, requests

for attempt in range(5):
    r = requests.post(url, json=data)
    if r.status_code == 429:
        time.sleep(2 ** attempt)
        continue
    r.raise_for_status()
    break`}
          </pre>
        </section>
      </div>
    </div>
  );
}
