import { useParams, Link } from 'react-router-dom';
import { FileText, ArrowLeft, Download, CreditCard } from 'lucide-react';

interface InvoiceDetail {
  id: string;
  date: string;
  amount: number;
  status: 'paid' | 'pending' | 'failed';
  paymentMethod: string;
  customer: string;
  items: { description: string; qty: number; unitPrice: number }[];
}

const getInvoice = (id: string): InvoiceDetail => ({
  id,
  date: '2026-05-20',
  amount: 50,
  status: 'paid',
  paymentMethod: 'Credit Card',
  customer: 'NeXify AI User',
  items: [
    { description: 'API Credits Top-Up', qty: 1, unitPrice: 50 },
  ],
});

export default function BillingDetail() {
  const { id } = useParams<{ id: string }>();
  const invoice = id ? getInvoice(id) : null;

  const downloadPdf = () => {
    if (!invoice) return;
    const content = [
      `INVOICE: ${invoice.id}`,
      `Date: ${invoice.date}`,
      `Amount: €${invoice.amount.toFixed(2)}`,
      `Status: ${invoice.status}`,
      `Customer: ${invoice.customer}`,
      `Payment Method: ${invoice.paymentMethod}`,
    ].join('\n');
    const blob = new Blob([content], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `invoice-${invoice.id}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!invoice) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-white">Invoice Not Found</h1>
        <Link to="/admin/billing" className="mt-4 inline-flex items-center gap-2 text-primary-400 hover:underline">
          <ArrowLeft className="h-4 w-4" /> Back to Billing History
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
      <Link to="/admin/billing" className="inline-flex items-center gap-2 text-sm text-[#9ca3af] hover:text-white mb-8">
        <ArrowLeft className="h-4 w-4" /> Back to Billing History
      </Link>

      <div className="rounded-lg border border-white/10 bg-surface-800 p-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <FileText className="h-6 w-6 text-primary-400" /> Invoice
          </h1>
          <span className="rounded-full bg-green-500/10 px-3 py-1 text-sm font-medium text-green-400">
            {invoice.status}
          </span>
        </div>

        <div className="mt-6 grid gap-4 border-t border-white/10 pt-6">
          <div className="flex justify-between">
            <span className="text-sm text-[#9ca3af]">Invoice Number</span>
            <span className="font-mono text-sm text-white">{invoice.id}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-[#9ca3af]">Date</span>
            <span className="text-sm text-white">{invoice.date}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-[#9ca3af]">Customer</span>
            <span className="text-sm text-white">{invoice.customer}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-[#9ca3af]">Payment Method</span>
            <span className="text-sm text-white">{invoice.paymentMethod}</span>
          </div>
        </div>

        <div className="mt-6 border-t border-white/10 pt-6">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[#9ca3af]">
                <th className="pb-2 font-medium">Item</th>
                <th className="pb-2 font-medium text-right">Qty</th>
                <th className="pb-2 font-medium text-right">Unit Price</th>
                <th className="pb-2 font-medium text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              {invoice.items.map((item, i) => (
                <tr key={i} className="border-t border-white/5">
                  <td className="py-2 text-white">{item.description}</td>
                  <td className="py-2 text-right text-[#dee3ed]">{item.qty}</td>
                  <td className="py-2 text-right text-[#dee3ed]">€{item.unitPrice.toFixed(2)}</td>
                  <td className="py-2 text-right font-medium text-white">€{(item.qty * item.unitPrice).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-6 flex items-center justify-between border-t border-white/10 pt-6">
          <span className="text-lg font-bold text-white">Total</span>
          <span className="text-2xl font-bold text-gold-500">€{invoice.amount.toFixed(2)}</span>
        </div>

        <button
          onClick={downloadPdf}
          className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-primary-500 py-3 text-sm font-semibold text-white hover:bg-primary-600"
        >
          <Download className="h-4 w-4" /> Download Invoice (PDF)
        </button>
      </div>

      <div className="mt-6 rounded-lg border border-white/10 bg-surface-800 p-4 flex items-center gap-3">
        <CreditCard className="h-5 w-5 text-[#9ca3af]" />
        <p className="text-sm text-[#9ca3af]">Need help? Contact billing@nexifyai.cloud for invoice-related inquiries.</p>
      </div>
    </div>
  );
}
