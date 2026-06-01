import ModelCard from '../components/ModelCard';

const allModels = [
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
  {
    name: 'NeXify-Mega',
    description:
      'Balanced model for enterprise chat and code generation. 14B parameters, 32K context.',
  },
  {
    name: 'NeXify-Coder',
    description:
      'Advanced code model fine-tuned for software development. Handles multi-file refactors and debugging.',
  },
];

export default function Models() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-white">Model Catalog</h1>
      <p className="mt-2 text-[#9ca3af]">
        All models accessible via NeXify API. Same pricing: €9/min input, €15/min output.
      </p>
      <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {allModels.map((m) => (
          <ModelCard key={m.name} name={m.name} description={m.description} />
        ))}
      </div>
    </div>
  );
}
