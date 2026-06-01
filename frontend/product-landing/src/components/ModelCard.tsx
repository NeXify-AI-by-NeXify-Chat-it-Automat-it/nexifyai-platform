import { Link } from 'react-router-dom';

interface ModelCardProps {
  name: string;
  description: string;
  href?: string;
}

export default function ModelCard({ name, description, href = '#' }: ModelCardProps) {
  return (
    <div className="rounded-lg border border-white/10 bg-surface-800 p-6 hover:shadow-lg transition-shadow">
      <h3 className="text-lg font-semibold text-white">{name}</h3>
      <p className="mt-2 text-sm text-[#9ca3af]">{description}</p>
      <Link
        to={href}
        className="mt-4 inline-block rounded-md bg-primary-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-primary-600"
      >
        View Details
      </Link>
    </div>
  );
}
