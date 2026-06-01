import { useState } from 'react';
import { Key, KeyRound, Copy, Check, Trash2, Plus } from 'lucide-react';

interface ApiKeyRecord {
  id: string;
  name: string;
  key: string;
  created: string;
}

export default function APIKeys() {
  const [keys, setKeys] = useState<ApiKeyRecord[]>([
    { id: '1', name: 'Production', key: 'sk-nexify-a1b2c3d4e5f6a7b8c9d0', created: '2026-05-01' },
    { id: '2', name: 'Development', key: 'sk-nexify-f6e5d4c3b2a1f0e9d8c7', created: '2026-05-10' },
  ]);
  const [newKeyName, setNewKeyName] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [generatedKey, setGeneratedKey] = useState<string | null>(null);

  const generateKey = () => {
    if (!newKeyName.trim()) return;
    const key = 'sk-nexify-' + crypto.randomUUID().replace(/-/g, '').slice(0, 24);
    setGeneratedKey(key);
    setKeys((prev) => [
      ...prev,
      { id: crypto.randomUUID(), name: newKeyName.trim(), key, created: new Date().toISOString().split('T')[0] },
    ]);
    setNewKeyName('');
  };

  const revokeKey = (id: string) => {
    setKeys((prev) => prev.filter((k) => k.id !== id));
  };

  const copyKey = async (key: string, id: string) => {
    await navigator.clipboard.writeText(key);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-white flex items-center gap-2">
        <Key className="h-6 w-6 text-primary-400" /> API Keys
      </h1>

      {/* Generate Section */}
      <section className="mt-8 rounded-lg border border-white/10 bg-surface-800 p-6">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Plus className="h-5 w-5 text-gold-500" /> Generate New Key
        </h2>
        <div className="mt-4 flex gap-3">
          <input
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            placeholder="e.g. Production, Development"
            className="flex-1 rounded border border-white/10 bg-surface-700 px-3 py-2 text-sm text-[#dee3ed] placeholder-[#9ca3af]"
          />
          <button
            onClick={generateKey}
            className="rounded bg-primary-500 px-4 py-2 text-sm font-medium text-white hover:bg-primary-600"
          >
            Generate
          </button>
        </div>
        {generatedKey && (
          <div className="mt-4 rounded-lg border border-gold-500/30 bg-surface-700 p-4">
            <p className="text-sm font-semibold text-gold-500">New key generated — copy it now. It won't be shown again.</p>
            <code className="mt-2 block break-all text-sm text-white">{generatedKey}</code>
          </div>
        )}
      </section>

      {/* List Section */}
      <section className="mt-8 space-y-3">
        {keys.map((k) => (
          <div key={k.id} className="flex items-center justify-between rounded-lg border border-white/10 bg-surface-800 p-4">
            <div>
              <p className="font-medium text-white">{k.name}</p>
              <code className="text-sm text-[#9ca3af]">{k.key.slice(0, 16)}...{k.key.slice(-4)}</code>
              <p className="mt-1 text-xs text-[#6b7280]">Created {k.created}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => copyKey(k.key, k.id)}
                className="rounded bg-surface-700 p-2 text-[#9ca3af] hover:bg-surface-600 hover:text-white"
              >
                {copiedId === k.id ? <Check className="h-4 w-4 text-green-400" /> : <Copy className="h-4 w-4" />}
              </button>
              <button
                onClick={() => revokeKey(k.id)}
                className="rounded bg-red-500/10 p-2 text-red-400 hover:bg-red-500/20"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}
