interface PricingCardProps {
  title: string;
  inputPrice: string;
  outputPrice: string;
  features: string[];
  highlighted?: boolean;
}

export default function PricingCard({
  title,
  inputPrice,
  outputPrice,
  features,
  highlighted = false,
}: PricingCardProps) {
  return (
    <div
      className={`relative rounded-lg border p-6 ${
        highlighted
          ? 'border-gold-500 bg-surface-800 ring-2 ring-gold-500/30'
          : 'border-white/10 bg-surface-800'
      }`}
    >
      {highlighted && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-gold-500 px-3 py-0.5 text-xs font-semibold text-black">
          Popular
        </span>
      )}
      <h3 className="text-lg font-semibold text-white">{title}</h3>
      <div className="mt-4 space-y-2">
        <div className="flex items-baseline justify-between">
          <span className="text-sm text-[#9ca3af]">Input</span>
          <span className="text-lg font-bold text-gold-500">{inputPrice}</span>
        </div>
        <div className="flex items-baseline justify-between">
          <span className="text-sm text-[#9ca3af]">Output</span>
          <span className="text-lg font-bold text-gold-500">{outputPrice}</span>
        </div>
      </div>
      <ul className="mt-4 space-y-2">
        {features.map((f, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-[#9ca3af]">
            <svg className="mt-0.5 h-4 w-4 shrink-0 text-green-400" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
            {f}
          </li>
        ))}
      </ul>
      <button className="mt-6 w-full rounded-lg bg-primary-500 py-2 text-sm font-semibold text-white hover:bg-primary-600">
        Get Started
      </button>
    </div>
  );
}
