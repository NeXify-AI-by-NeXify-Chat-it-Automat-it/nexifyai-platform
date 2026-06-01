import { FileText, Download } from 'lucide-react';
import { Link } from 'react-router-dom';

interface Invoice {
  id: string;
  date: string;
  amount: number;
  status: 'paid' | 'pending' | 'failed';
}

const invoices: Invoice[] = [
  { id: 'INV-A1B2C3', date: '2026-05-20', amount: 50, status: 'paid' },
  { id: 'INV-D4E5F6', date: '2026-05-10', amount: 100, status: 'paid' },
  { id: 'INV-G7H8I9', date: '2026-04-28', amount: 25, status: 'paid' },
  { id: 'INV-J0K1L2', date: '2026-04-15', amount: 75, status: 'failed' },
];

export default function BillingHistory() {
  const downloadInvoice = (inv: Invoice) => {
    const content = [
      `INVOICE: ${inv.id}`,
      `Date: ${inv.date}`,
      `Amount: €${inv.amount.toFixed(2)}`,
      `Status: ${inv.status}`,
      `Customer: NeXify AI User`,
    ].join('\n');
    const blob = new Blob([content], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `invoice-${inv.id}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const statusColor = (s: string) => {
    switch (s) {
      case 'paid': return 'text-green-400';
      case 'pending': return 'text-gold-500';
      case 'failed': return 'text-red-400';
      default: return 'text-[#9ca3af]';
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-white flex items-center gap-2">
        <FileText className="h-6 w-6 text-primary-400" /> Billing History
      </h1>

      <section className="mt-8">
        <div className="overflow-x-auto rounded-lg border border-white/10">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-surface-800 text-left text-[#9ca3af]">
                <th className="px-4 py-3 font-medium">Invoice</th>
                <th className="px-4 py-3 font-medium">Date</th>
                <th className="px-4 py-3 font-medium">Amount</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {invoices.map((inv) => (
                <tr key={inv.id} className="hover:bg-surface-800">
                  <td className="px-4 py-3 font-mono text-sm text-primary-300">{inv.id}</td>
                  <td className="px-4 py-3 text-[#dee3ed]">{inv.date}</td>
                  <td className="px-4 py-3 text-gold-500 font-medium">€{inv.amount.toFixed(2)}</td>
                  <td className={`px-4 py-3 font-medium ${statusColor(inv.status)}`}>{inv.status}</td>
                  <td className="px-4 py-3 flex gap-2">
                    <Link
                      to={`/admin/billing/${inv.id}`}
                      className="rounded bg-surface-700 px-3 py-1 text-xs text-[#9ca3af] hover:text-white"
                    >
                      View
                    </Link>
                    <button
                      onClick={() => downloadInvoice(inv)}
                      className="flex items-center gap-1 rounded bg-surface-700 px-3 py-1 text-xs text-[#9ca3af] hover:text-white"
                    >
                      <Download className="h-3 w-3" /> PDF
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
