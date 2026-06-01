import { useState } from 'react';
import { CreditCard, Euro, ArrowRight } from 'lucide-react';

const paymentMethods = ['Credit Card', 'SEPA Bank Transfer', 'PayPal'];

export default function TopUp() {
  const [amount, setAmount] = useState<number>(50);
  const [method, setMethod] = useState(paymentMethods[0]);
  const [processing, setProcessing] = useState(false);
  const [invoice, setInvoice] = useState<string | null>(null);

  const minAmount = 9;

  const handleTopUp = async () => {
    if (amount < minAmount) return;
    setProcessing(true);

    // Simulate top-up and invoice generation
    await new Promise((r) => setTimeout(r, 1500));

    const invoiceId = 'INV-' + Date.now().toString(36).toUpperCase();
    setInvoice(invoiceId);

    // Generate a simple text representation of invoice (in production would be PDF)
    const invoiceData = [
      `INVOICE: ${invoiceId}`,
      `Date: ${new Date().toISOString().split('T')[0]}`,
      `Amount: €${amount.toFixed(2)}`,
      `Payment Method: ${method}`,
      `Status: Paid`,
      `Customer: NeXify AI User`,
    ].join('\n');

    // Trigger download of invoice text file (simulate PDF)
    const blob = new Blob([invoiceData], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `invoice-${invoiceId}.pdf`;
    a.click();
    URL.revokeObjectURL(url);

    setProcessing(false);
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-white flex items-center gap-2">
        <CreditCard className="h-6 w-6 text-primary-400" /> Top Up Wallet
      </h1>

      <section className="mt-8 rounded-lg border border-white/10 bg-surface-800 p-6">
        <h2 className="text-lg font-semibold text-white">Add Credits</h2>

        <div className="mt-4">
          <label className="text-sm text-[#9ca3af]">Amount (€) - minimum €{minAmount}</label>
          <div className="mt-1 flex items-center gap-2 rounded border border-white/10 bg-surface-700 px-3 py-2">
            <Euro className="h-5 w-5 text-[#9ca3af]" />
            <input
              type="number"
              min={minAmount}
              value={amount}
              onChange={(e) => setAmount(Math.max(minAmount, Number(e.target.value) || 0))}
              className="w-full bg-transparent text-lg font-bold text-white outline-none"
            />
          </div>
          <div className="mt-2 flex gap-2">
            {[10, 25, 50, 100, 250].map((v) => (
              <button
                key={v}
                onClick={() => setAmount(v)}
                className={`rounded px-3 py-1 text-sm font-medium ${amount === v ? 'bg-primary-500 text-white' : 'bg-surface-700 text-[#9ca3af] hover:text-white'}`}
              >
                €{v}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-6">
          <label className="text-sm text-[#9ca3af]">Payment Method</label>
          <select
            value={method}
            onChange={(e) => setMethod(e.target.value)}
            className="mt-1 w-full rounded border border-white/10 bg-surface-700 px-3 py-2 text-sm text-white"
          >
            {paymentMethods.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>

        <button
          onClick={handleTopUp}
          disabled={processing || amount < minAmount}
          className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-primary-500 py-3 text-sm font-semibold text-white hover:bg-primary-600 disabled:opacity-50"
        >
          {processing ? 'Processing...' : 'Confirm Top Up'}
          <ArrowRight className="h-4 w-4" />
        </button>

        {invoice && (
          <div className="mt-4 rounded-lg border border-green-500/30 bg-green-500/10 p-4">
            <p className="font-medium text-green-400">Payment successful!</p>
            <p className="mt-1 text-sm text-[#9ca3af]">Invoice {invoice} downloaded automatically.</p>
          </div>
        )}
      </section>
    </div>
  );
}
