import { Link } from 'react-router-dom';
import ModelCard from '../components/ModelCard';
import PricingCard from '../components/PricingCard';

const models = [
  {
    name: 'NeXify-Mega',
    description:
      'General-purpose reasoning model with 128K context window. Ideal for chat, analysis, and code generation.',
  },
  {
    name: 'NeXify-Coder',
    description:
      'Code-optimized model fine-tuned for programming tasks. Supports multiple languages and 64K context.',
  },
  {
    name: 'NeXify-Swift',
    description:
      'Lightweight conversational model from NeXify. Fast inference, cost-effective for high-throughput apps.',
  },
  {
    name: 'NeXify-Supreme',
    description:
      'Large-scale language model with 70B parameters. Best for complex reasoning and enterprise workloads.',
  },
];

const pricingPlans = [
  {
    title: 'Starter',
    inputPrice: '€9/min',
    outputPrice: '€15/min',
    features: ['1,000 free tokens', 'Shared instances', 'Standard support'],
  },
  {
    title: 'Pro',
    inputPrice: '€9/min',
    outputPrice: '€15/min',
    features: [
      '100,000 tokens included',
      'Priority throughput',
      'Email support',
      'API rate limit increased',
    ],
    highlighted: true,
  },
  {
    title: 'Enterprise',
    inputPrice: '€9/min',
    outputPrice: '€15/min',
    features: [
      'Custom token volume',
      'Dedicated instances',
      'SLA & priority support',
      'SSO / SAML',
      'On-premise option',
    ],
  },
];

export default function Landing() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden px-4 py-24 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <h1 className="text-5xl font-extrabold tracking-tight text-white sm:text-6xl">
            AI APIs for{' '}
            <span className="bg-gradient-to-r from-primary-400 to-gold-500 bg-clip-text text-transparent">
              NeXify & NeXify
            </span>
          </h1>
          <p className="mt-6 text-lg leading-relaxed text-[#9ca3af]">
            Access the latest LLMs through a single API. Buy tokens by the minute,
            integrate in minutes, and scale with enterprise-grade infrastructure.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link
              to="/register"
              className="rounded-lg bg-primary-500 px-6 py-3 text-base font-semibold text-white hover:bg-primary-600 transition-colors"
            >
              Start Free Trial
            </Link>
            <Link
              to="/docs"
              className="rounded-lg border border-white/10 px-6 py-3 text-base font-medium text-[#dee3ed] hover:bg-white/5 transition-colors"
            >
              View Documentation
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="border-t border-white/10 px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <h2 className="text-center text-3xl font-bold text-white">
            Why developers choose NeXify AI
          </h2>
          <div className="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {[
              {
                title: 'Single API',
                desc: 'Unified endpoint for NeXify and NeXify models. No vendor lock-in.',
              },
              {
                title: 'Token Pricing',
                desc: 'Pay per minute of input/output usage. Predictable costs, no surprises.',
              },
              {
                title: 'Enterprise SLA',
                desc: '99.9% uptime, dedicated instances, and priority support for teams.',
              },
              {
                title: 'Fast Inference',
                desc: 'Optimized runtimes on GPU clusters for sub-second latency.',
              },
              {
                title: 'Secure by Default',
                desc: 'Encrypted in transit and at rest. SOC 2 compliant infrastructure.',
              },
              {
                title: 'Developer Tools',
                desc: 'OpenAPI spec, SDKs for Python and Node.js, and interactive API explorer.',
              },
            ].map((f, i) => (
              <div key={i} className="rounded-lg border border-white/10 p-6">
                <h3 className="text-base font-semibold text-white">{f.title}</h3>
                <p className="mt-2 text-sm text-[#9ca3af]">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="border-t border-white/10 px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <h2 className="text-center text-3xl font-bold text-white">
            Simple, transparent pricing
          </h2>
          <p className="mt-4 text-center text-[#9ca3af]">
            €9/min input · €15/min output. Same rate for all models.
          </p>
          <div className="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {pricingPlans.map((plan) => (
              <PricingCard key={plan.title} {...plan} />
            ))}
          </div>
        </div>
      </section>

      {/* Model Catalog Preview */}
      <section className="border-t border-white/10 px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <div className="flex items-center justify-between">
            <h2 className="text-3xl font-bold text-white">Explore models</h2>
            <Link
              to="/models"
              className="text-sm font-medium text-primary-400 hover:text-primary-300"
            >
              View all →
            </Link>
          </div>
          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {models.map((m) => (
              <ModelCard key={m.name} name={m.name} description={m.description} />
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-white/10 px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-bold text-white">
            Ready to build with NeXify AI?
          </h2>
          <p className="mt-4 text-[#9ca3af]">
            Create an account, get your API key, and start making requests in under two minutes.
          </p>
          <div className="mt-8">
            <Link
              to="/register"
              className="rounded-lg bg-primary-500 px-6 py-3 text-base font-semibold text-white hover:bg-primary-600 transition-colors"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
