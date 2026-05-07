import React from 'react';
import { useParams } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useLanguage } from '../i18n/LanguageContext';
import T from '../i18n/translations';
import SEOHead from '../components/SEOHead';
import { COMPANY, LEGAL_PATHS, Logo, I, Footer } from '../components/shared';
import { getPost, getMeta } from '../data/blog';
import '../App.css';

const BASE_URL = 'https://www.nexify-automate.com';

export default function BlogPostPage() {
  const { lang, slug } = useParams();
  const t = T[lang] || T.de;
  const post = getPost(slug, lang);
  const m = getMeta(slug, lang);
  const lp = LEGAL_PATHS[lang] || LEGAL_PATHS.de;
  const thisYear = new Date().getFullYear();

  if (!post) {
    return (
      <div className="app" style={{ padding: '8rem 2rem', textAlign: 'center' }}>
        <h1>{lang === 'en' ? 'Post not found' : lang === 'nl' ? 'Pagina niet gevonden' : 'Artikel nicht gefunden'}</h1>
        <a href={`/${lang}/blog`} className="btn btn-primary" style={{ marginTop: '2rem', display: 'inline-block' }}>
          {lang === 'en' ? 'Back to Blog' : lang === 'nl' ? 'Terug naar blog' : 'Zurück zum Blog'}
        </a>
      </div>
    );
  }

  const canonical = `${BASE_URL}/${lang}/blog/${slug}`;
  const breadcrumb = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: `${BASE_URL}/${lang}` },
      { '@type': 'ListItem', position: 2, name: 'Blog', item: `${BASE_URL}/${lang}/blog` },
      { '@type': 'ListItem', position: 3, name: m?.title || post.meta?.title || slug, item: canonical }
    ]
  };

  const blogSchema = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: m?.title || post.meta?.title,
    description: m?.description || post.meta?.description,
    datePublished: post.published,
    author: { '@type': 'Organization', name: 'NeXifyAI by NeXify' },
    publisher: { '@type': 'Organization', name: 'NeXifyAI by NeXify', logo: `${BASE_URL}/nexifyai-logo-light.png` },
    mainEntityOfPage: canonical,
    image: `${BASE_URL}/og-image.png`
  };

  const page = m?.title || post.meta?.title || 'Blog';

  return (
    <div className="app">
      <SEOHead lang={lang} page="blog" />
      <Helmet>
        <title>{m?.title || 'Blog'}</title>
        <meta name="description" content={m?.description || 'Blog article'} />
        <meta name="keywords" content={post.meta?.keywords || ''} />
        <meta property="og:title" content={m?.title || 'Blog'} />
        <meta property="og:description" content={m?.description || 'Blog article'} />
        <meta property="og:url" content={canonical} />
        <meta name="twitter:title" content={m?.title || 'Blog'} />
        <meta name="twitter:description" content={m?.description || 'Blog article'} />
        <link rel="canonical" href={canonical} />
        <script type="application/ld+json">{JSON.stringify(breadcrumb)}</script>
        <script type="application/ld+json">{JSON.stringify(blogSchema)}</script>
      </Helmet>

      <nav className="nav scrolled" role="navigation">
        <div className="container nav-inner">
          <a href={`/${lang}`} className="nav-logo"><Logo /></a>
          <div className="nav-actions">
            <a href={`/${lang}/blog`} className="btn btn-ghost">
              ← {lang === 'en' ? 'Blog' : lang === 'nl' ? 'Blog' : 'Blog'}
            </a>
          </div>
        </div>
      </nav>

      <main id="main-content">
        <article className="section bg-dark" style={{ paddingTop: '8rem' }}>
          <div className="container" style={{ maxWidth: 800, margin: '0 auto' }}>
            <div style={{ marginBottom: '2rem' }}>
              <span style={{ color: '#FE9B7B', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 600 }}>{post.category}</span>
              <span style={{ color: '#8892a0', fontSize: '0.85rem', marginLeft: '1rem' }}>{post.published} · {post.readTime}</span>
            </div>
            <h1 style={{ fontSize: 'clamp(1.8rem,3.5vw,2.5rem)', fontWeight: 800, lineHeight: 1.2, marginBottom: '2rem' }}>
              {m?.title || 'Blog'}
            </h1>
            <div className="blog-content" style={{
              lineHeight: 1.8, fontSize: '1.05rem', color: '#c8ced9'
            }} dangerouslySetInnerHTML={{ __html: post.body }} />
            <hr style={{ border: 'none', borderTop: '1px solid rgba(255,255,255,0.08)', margin: '3rem 0' }} />
            <div style={{ textAlign: 'center' }}>
              <p style={{ color: '#8892a0', marginBottom: '1.5rem' }}>
                {lang === 'en' ? 'Want to learn more? Book a free consultation.' :
                 lang === 'nl' ? 'Meer weten? Boek een gratis adviesgesprek.' :
                 'Mehr erfahren? Vereinbaren Sie ein kostenloses Beratungsgespräch.'}
              </p>
              <a href="/termin" className="btn btn-primary btn-lg btn-glow">
                {lang === 'en' ? 'Book Consultation' : lang === 'nl' ? 'Adviesgesprek boeken' : 'Beratung buchen'}
              </a>
              <div style={{ marginTop: '1rem' }}>
                <a href={`/${lang}/blog`} style={{ color: '#FE9B7B', fontSize: '0.9rem' }}>
                  ← {lang === 'en' ? 'All articles' : lang === 'nl' ? 'Alle artikelen' : 'Alle Artikel'}
                </a>
              </div>
            </div>
          </div>
        </article>
      </main>
      <Footer onCookieSettings={() => {}} t={t} lang={lang} />
    </div>
  );
};
