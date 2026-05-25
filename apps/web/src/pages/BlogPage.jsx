import React from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useLanguage } from '../i18n/LanguageContext';
import T from '../i18n/translations';
import SEOHead from '../components/SEOHead';
import { COMPANY, LEGAL_PATHS, Logo, I, Footer } from '../components/shared';
import { getAllPosts } from '../data/blog';
import '../App.css';

const META = {
  de: { title: 'Blog — KI-Wissen für Unternehmen | NeXifyAI',
    description: 'Praktisches KI-Wissen für den DACH-Mittelstand: KI-Agenten, Prozessautomation, CRM-Integration, RAG-Wissenssysteme, DSGVO, ROI und mehr.',
    keywords: 'KI-Blog, KI-Wissen, KI-Agenten Blog, Prozessautomation Blog, CRM Integration Blog, DACH Mittelstand KI' },
  nl: { title: 'Blog — AI-Kennis voor Bedrijven | NeXifyAI',
    description: 'Praktische AI-kennis voor bedrijven: AI-agenten, procesautomatisering, CRM-integratie, RAG-kennissystemen, AVG en meer.',
    keywords: 'AI-blog, AI-kennis, AI-agenten blog, procesautomatisering blog' },
  en: { title: 'Blog — AI Knowledge for Business | NeXifyAI',
    description: 'Practical AI knowledge for businesses: AI agents, process automation, CRM integration, RAG knowledge systems, GDPR, ROI and more.',
    keywords: 'AI blog, AI knowledge, AI agents blog, process automation blog' }
};

export default function BlogPage() {
  const { lang } = useLanguage();
  const t = T[lang] || T.de;
  const m = META[lang] || META.de;
  const lp = LEGAL_PATHS[lang] || LEGAL_PATHS.de;
  const thisYear = new Date().getFullYear();
  const posts = getAllPosts(lang);
  const postsAll = getAllPosts('de'); // fallback count

  const blogSchema = {
    '@context': 'https://schema.org', '@type': 'Blog',
    name: m.title, description: m.description,
    blogPost: posts.map(p => ({
      '@type': 'BlogPosting',
      headline: p.meta.title,
      description: p.meta.description,
      url: `https://nexifyai.cloud/${lang}/blog/${p.slug}`,
      datePublished: p.published,
      author: { '@type': 'Organization', name: 'NeXifyAI' }
    }))
  };

  return (
    <div className="app">
      <SEOHead lang={lang} page="blog" />
      <Helmet>
        <title>{m.title}</title>
        <meta name="description" content={m.description} />
        <meta name="keywords" content={m.keywords} />
        <meta property="og:title" content={m.title} />
        <meta property="og:description" content={m.description} />
        <meta name="twitter:title" content={m.title} />
        <meta name="twitter:description" content={m.description} />
        <script type="application/ld+json">{JSON.stringify(blogSchema)}</script>
      </Helmet>

      <nav className="nav scrolled" role="navigation">
        <div className="container nav-inner">
          <a href={`/${lang}`} className="nav-logo"><Logo /></a>
          <div className="nav-actions">
            <a href={`/${lang}`} className="btn btn-ghost">
              {lang === 'en' ? 'Back to Home' : lang === 'nl' ? 'Terug naar home' : 'Zurück zur Startseite'}
            </a>
          </div>
        </div>
      </nav>

      <main id="main-content">
        <section className="section bg-dark" style={{ paddingTop: '8rem' }}>
          <div className="container">
            <div className="section-header" style={{ textAlign: 'center', marginBottom: '4rem' }}>
              <span className="label">BLOG</span>
              <h1 style={{ fontSize: 'clamp(2rem,4vw,3rem)', fontWeight: 800, marginTop: '0.5rem' }}>
                {lang === 'en' ? 'AI Knowledge for Business' : lang === 'nl' ? 'AI-Kennis voor Bedrijven' : 'KI-Wissen für Unternehmen'}
              </h1>
              <p className="section-subtitle">
                {lang === 'en' ? 'Practical insights, guides, and best practices.' :
                 lang === 'nl' ? 'Praktische inzichten, gidsen en best practices.' :
                 'Praktische Einblicke, Leitfäden und Best Practices.'}
              </p>
            </div>

            <div className="solutions-grid" role="list">
              {posts.map((p, i) => (
                <a key={i} href={`/${lang}/blog/${p.slug}`} className="sol-card" role="listitem" style={{ textDecoration: 'none', textAlign: 'left', display: 'flex', flexDirection: 'column' }}>
                  <span style={{ fontSize: '0.75rem', color: '#FE9B7B', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 600 }}>{p.category}</span>
                  <h2 className="sol-title" style={{ fontSize: '1.2rem', marginTop: '0.5rem', color: '#dee3ed' }}>{p.meta.title}</h2>
                  <p className="sol-desc" style={{ flex: 1 }}>{p.meta.description}</p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem' }}>
                    <span style={{ fontSize: '0.85rem', color: '#8892a0' }}>{p.published} · {p.readTime}</span>
                    <span style={{ fontSize: '0.85rem', color: '#FE9B7B' }}>
                      {lang === 'en' ? 'Read →' : lang === 'nl' ? 'Lees →' : 'Lesen →'}
                    </span>
                  </div>
                  <div className="sol-bar"></div>
                </a>
              ))}
            </div>
          </div>
        </section>
      </main>
      <Footer onCookieSettings={() => {}} t={t} lang={lang} />
    </div>
  );
};
