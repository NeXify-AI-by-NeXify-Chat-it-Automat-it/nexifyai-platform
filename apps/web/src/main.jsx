/* Build 2026-05-17T17:16:59.210533 */
// P0: Runtime diagnostics — must be first import
import './observability/frontend/runtime_error_capture';
import React from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { LanguageProvider } from './i18n/LanguageContext';
import ErrorBoundary from './components/ErrorBoundary';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import Admin from './pages/Admin';
import LegalPage from './pages/LegalPages';
import QuotePortal from './pages/QuotePortal';
import CustomerPortal from './pages/CustomerPortal';
import IntegrationDetail from './pages/IntegrationDetail';
import UnifiedLogin from './pages/UnifiedLogin';
import BookingPage from './pages/BookingPage';
import ContractAcceptance from './pages/ContractAcceptance';
import LeistungenPage from './pages/LeistungenPage';
import PreisePage from './pages/PreisePage';
import KontaktPage from './pages/KontaktPage';
import BlogPage from './pages/BlogPage';
import BlogPostPage from './pages/BlogPostPage';

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

/* Wrapper to inject providers */
function RootLayout({ children }) {
  return (
    <HelmetProvider>
      <LanguageProvider>
        <ErrorBoundary>
          {children}
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
  /* Agentur alternative access paths (see sitemap.xml) */
  { path: '/agentur', element: <RootLayout><App /></RootLayout> },
  { path: '/agentur/leistungen', element: <RootLayout><LeistungenPage /></RootLayout> },
  { path: '/agentur/preise', element: <RootLayout><PreisePage /></RootLayout> },
  { path: '/agentur/kontakt', element: <RootLayout><KontaktPage /></RootLayout> },
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
