export default function Footer() {
  return (
    <footer className="border-t border-white/10 bg-surface-800">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Product</h3>
            <ul className="mt-3 space-y-2">
              <li><a href="/models" className="text-sm text-[#9ca3af] hover:text-white transition-colors">Models</a></li>
              <li><a href="/docs" className="text-sm text-[#9ca3af] hover:text-white transition-colors">Docs</a></li>
              <li><a href="/pricing" className="text-sm text-[#9ca3af] hover:text-white transition-colors">Pricing</a></li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Resources</h3>
            <ul className="mt-3 space-y-2">
              <li><a href="/docs" className="text-sm text-[#9ca3af] hover:text-white transition-colors">API Reference</a></li>
              <li><a href="/docs" className="text-sm text-[#9ca3af] hover:text-white transition-colors">SDKs</a></li>
              <li><a href="/docs" className="text-sm text-[#9ca3af] hover:text-white transition-colors">Changelog</a></li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Company</h3>
            <ul className="mt-3 space-y-2">
              <li><span className="text-sm text-[#9ca3af]">About</span></li>
              <li><span className="text-sm text-[#9ca3af]">Blog</span></li>
              <li><span className="text-sm text-[#9ca3af]">Contact</span></li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Legal</h3>
            <ul className="mt-3 space-y-2">
              <li><span className="text-sm text-[#9ca3af]">Privacy</span></li>
              <li><span className="text-sm text-[#9ca3af]">Terms</span></li>
            </ul>
          </div>
        </div>
        <div className="mt-8 border-t border-white/10 pt-6 text-center">
          <p className="text-sm text-[#6b7280]">&copy; {new Date().getFullYear()} NeXify AI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
