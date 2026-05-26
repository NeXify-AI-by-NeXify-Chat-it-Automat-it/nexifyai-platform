/* Build 2026-05-26T20:27:00 */
// P0: Runtime diagnostics — must be first import
import './observability/frontend/runtime_error_capture';
import React, { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { LanguageProvider } from './i18n/LanguageContext';
import ErrorBoundary from './components/ErrorBoundary';
import ReactDOM from 'react-dom/client';
import './index.css';

// Eager: lightweight pages (homepage, services, pricing, contact)
import App from './App';
import LeistungenPage from './pages/LeistungenPage';
import PreisePage from './pages/PreisePage';
import KontaktPage from './pages/KontaktPage';
import UnifiedLogin from './pages/UnifiedLogin';
import BookingPage from './pages/BookingPage';

// Lazy: heavy pages (admin, portal, blog, legal, integrations)
const Admin = lazy(() => import('./pages/Admin'));
const LegalPage = lazy(() => import('./pages/LegalPages'));
const QuotePortal = lazy(() => import('./pages/QuotePortal'));
const CustomerPortal = lazy(() => import('./pages/CustomerPortal'));
const IntegrationDetail = lazy(() => import('./pages/IntegrationDetail'));
const ContractAcceptance = lazy(() => import('./pages/ContractAcceptance'));
const BlogPage = lazy(() => import('./pages/BlogPage'));
const BlogPostPage = lazy(() => import('./pages/BlogPostPage'));

/* Language-aware redirect */
function LangRedirect() {
  const stored = localStorage.getItem('nx_lang');
  const lang = stored && ['de', 'nl', 'en'].includes(stored) ? stored : 'de';
  return <Navigate to={`/${lang}`} replace />;
}

function LegacyRedirect({ slug }) {
  const stored = localStorage.getItem('nx_lang');
  const lang = stored && ['de', 'nl', 'en'].includes(stored) ? stored : 'de';
  return <Navigate to={`/${lang}/${slug}`} replace />;
}

/* Suspense fallback for lazy-loaded routes */
function LazyFallback() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', background: '#0d1117' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ width: 48, height: 48, border: '3px solid rgba(255,155,122,0.2)', borderTopColor: '#ff9b7a', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
        <p style={{ color: '#8f9095', marginTop: 16, fontSize: 14 }}>Laden…</p>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

/* Wrapper to inject providers */
function RootLayout({ children }) {
  return (
    <HelmetProvider>
      <LanguageProvider>
        <ErrorBoundary>
          <Suspense fallback={<LazyFallback />}>
            {children}
          </Suspense>
        </ErrorBoundary>
      </LanguageProvider>
    </HelmetProvider>
  );
}

const router = createBrowserRouter([
  { path: '/', element: <RootLayout><LangRedirect /></RootLayout> },
  { path: '/de', element: <RootLayout><App /></RootLayout> },
  { path: '/nl', element: <RootLayout><App /></RootLayout> },
  { path: '/en', element: <RootLayout><App /></RootLayout> },
  { path: '/:lang/kontakt', element: <RootLayout><KontaktPage /></RootLayout> },
  { path: '/:lang/contact', element: <RootLayout><KontaktPage /></RootLayout> },
  { path: '/:lang/leistungen', element: <RootLayout><LeistungenPage /></RootLayout> },
  { path: '/:lang/services', element: <RootLayout><LeistungenPage /></RootLayout> },
  { path: '/:lang/preise', element: <RootLayout><PreisePage /></RootLayout> },
  { path: '/:lang/pricing', element: <RootLayout><PreisePage /></RootLayout> },
  { path: '/:lang/portfolio', element: <RootLayout><LeistungenPage /></RootLayout> },
  { path: '/:lang/tarife', element: <RootLayout><PreisePage /></RootLayout> },
  { path: '/:lang/blog', element: <RootLayout><BlogPage /></RootLayout> },
  { path: '/:lang/blog/:slug', element: <RootLayout><BlogPostPage /></RootLayout> },
  { path: '/:lang/:page', element: <RootLayout><LegalPage /></RootLayout> },
  /* /agentur/ routes — agentur prefix */
  { path: '/agentur', element: <RootLayout><App /></RootLayout> },
  { path: '/agentur/leistungen', element: <RootLayout><LeistungenPage /></RootLayout> },
  { path: '/agentur/preise', element: <RootLayout><PreisePage /></RootLayout> },
  { path: '/agentur/kontakt', element: <RootLayout><KontaktPage /></RootLayout> },
  { path: '/blog', element: <RootLayout><BlogPage /></RootLayout> },
  { path: '/blog/:slug', element: <RootLayout><BlogPostPage /></RootLayout> },
  { path: '/login', element: <RootLayout><UnifiedLogin /></RootLayout> },
  { path: '/login/verify', element: <RootLayout><UnifiedLogin /></RootLayout> },
  { path: '/termin', element: <RootLayout><BookingPage /></RootLayout> },
  { path: '/booking', element: <RootLayout><BookingPage /></RootLayout> },
  { path: '/admin', element: <RootLayout><Admin /></RootLayout> },
  { path: '/integrationen/:slug', element: <RootLayout><IntegrationDetail /></RootLayout> },
  { path: '/angebot', element: <RootLayout><QuotePortal /></RootLayout> },
  { path: '/vertrag', element: <RootLayout><ContractAcceptance /></RootLayout> },
  { path: '/portal', element: <RootLayout><CustomerPortal /></RootLayout> },
  { path: '/portal/:token', element: <RootLayout><CustomerPortal /></RootLayout> },
  { path: '/portfolio', element: <RootLayout><LeistungenPage /></RootLayout> },
  { path: '/tarife', element: <RootLayout><PreisePage /></RootLayout> },
  { path: '/kontakt', element: <RootLayout><KontaktPage /></RootLayout> },
  { path: '/leistungen', element: <RootLayout><LeistungenPage /></RootLayout> },
  { path: '/preise', element: <RootLayout><PreisePage /></RootLayout> },
  { path: '/services', element: <RootLayout><LeistungenPage /></RootLayout> },
  { path: '/pricing', element: <RootLayout><PreisePage /></RootLayout> },
  { path: '/contact', element: <RootLayout><KontaktPage /></RootLayout> },
  { path: '/impressum', element: <RootLayout><LegacyRedirect slug="impressum" /></RootLayout> },
  { path: '/datenschutz', element: <RootLayout><LegacyRedirect slug="datenschutz" /></RootLayout> },
  { path: '/agb', element: <RootLayout><LegacyRedirect slug="agb" /></RootLayout> },
  { path: '/ki-hinweise', element: <RootLayout><LegacyRedirect slug="ki-hinweise" /></RootLayout> },
  { path: '*', element: <RootLayout><LangRedirect /></RootLayout> },
]);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
