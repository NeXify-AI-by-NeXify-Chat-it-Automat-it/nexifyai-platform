import React from 'react';
import { Helmet } from 'react-helmet-async';

const BASE_URL = 'https://www.nexify-automate.com';

const META = {
  de: {
    title: 'NeXifyAI — Intelligente KI-Agenten für Enterprise-Automatisierung | DACH',
    description: 'NeXifyAI entwickelt autonome KI-Agenten für DACH-Unternehmen. 400+ Integrationen, DSGVO-konform, Enterprise-Grade. Chat it. Automate it.',
    keywords: 'KI-Agenten, Enterprise Automatisierung, DACH, KI-Beratung, Prozessautomatisierung, GPT, LLM, SAP Integration, CRM Automatisierung'
  },
  nl: {
    title: 'NeXifyAI — Intelligente AI-Agenten voor Enterprise-Automatisering',
    description: 'NeXifyAI ontwikkelt autonome AI-agenten voor bedrijven. 400+ integraties, AVG-conform, enterprise-grade. Chat it. Automate it.',
    keywords: 'AI-agenten, Enterprise automatisering, AI-advies, procesautomatisering, GPT, LLM, SAP integratie, CRM automatisering'
  },
  en: {
    title: 'NeXifyAI — Intelligent AI Agents for Enterprise Automation',
    description: 'NeXifyAI builds autonomous AI agents for enterprise businesses. 400+ integrations, GDPR-compliant, enterprise-grade. Chat it. Automate it.',
    keywords: 'AI agents, enterprise automation, AI consulting, process automation, GPT, LLM, SAP integration, CRM automation'
  }
};

// Breadcrumb definitions per page
const BREADCRUMBS = {
  home: (lang) => ({ '@type': 'BreadcrumbList', itemListElement: [
    { '@type': 'ListItem', position: 1, name: { de: 'Startseite', nl: 'Home', en: 'Home' }[lang] || 'Home', item: `${BASE_URL}/${lang}` }
  ]}),
  leistungen: (lang) => ({ '@type': 'BreadcrumbList', itemListElement: [
    { '@type': 'ListItem', position: 1, name: 'Home', item: `${BASE_URL}/${lang}` },
    { '@type': 'ListItem', position: 2, name: { de: 'Leistungen', nl: 'Diensten', en: 'Services' }[lang] || 'Services', item: `${BASE_URL}/${lang}/leistungen` }
  ]}),
  preise: (lang) => ({ '@type': 'BreadcrumbList', itemListElement: [
    { '@type': 'ListItem', position: 1, name: 'Home', item: `${BASE_URL}/${lang}` },
    { '@type': 'ListItem', position: 2, name: { de: 'Preise & Tarife', nl: 'Prijzen & Tarieven', en: 'Pricing & Plans' }[lang] || 'Pricing', item: `${BASE_URL}/${lang}/preise` }
  ]}),
  kontakt: (lang) => ({ '@type': 'BreadcrumbList', itemListElement: [
    { '@type': 'ListItem', position: 1, name: 'Home', item: `${BASE_URL}/${lang}` },
    { '@type': 'ListItem', position: 2, name: { de: 'Kontakt', nl: 'Contact', en: 'Contact' }[lang] || 'Contact', item: `${BASE_URL}/${lang}/kontakt` }
  ]}),
  blog: (lang) => ({ '@type': 'BreadcrumbList', itemListElement: [
    { '@type': 'ListItem', position: 1, name: 'Home', item: `${BASE_URL}/${lang}` },
    { '@type': 'ListItem', position: 2, name: 'Blog', item: `${BASE_URL}/${lang}/blog` }
  ]}),
};

const LANG_MAP = { de: 'de-DE', nl: 'nl-NL', en: 'en-GB' };

// FAQ data extracted from translations
const FAQ_DATA = {
  de: [
    { q: 'Welche Tarife gibt es?', a: 'Wir bieten zwei aktive Kern-Tarife an: Starter AI Agenten AG (499 EUR/Monat) mit 2 KI-Agenten und Growth AI Agenten AG (1.299 EUR/Monat) mit 10 KI-Agenten. Beide mit 24 Monaten Laufzeit.' },
    { q: 'Was bedeutet 24 Monate Laufzeit?', a: 'Der Vertrag läuft über 24 Monate ab Beauftragung. Dies ermöglicht nachhaltige Implementierung, Optimierung und kontinuierliche Weiterentwicklung Ihrer KI-Agenten.' },
    { q: 'Wie funktioniert die 30-%-Aktivierungsanzahlung?', a: 'Bei Beauftragung wird eine Aktivierungsanzahlung von 30 % des Gesamtvertragswerts fällig. Diese deckt Projektstart, Priorisierung, Setup, Kapazitätsreservierung und Implementierungsfreigabe ab.' },
    { q: 'Was ist im Starter enthalten?', a: '2 KI-Agenten, Shared Cloud Infrastructure, E-Mail-Support (48h), Basis-Integrationen (REST API), Standard-Monitoring, monatliches Reporting. Gesamtvertragswert: 11.976 EUR (netto).' },
    { q: 'Was ist im Growth enthalten?', a: '10 KI-Agenten, Private Cloud Infrastructure, Priority Support (24h), CRM/ERP-Kit (SAP, HubSpot, Salesforce), Advanced Monitoring & Analytics, wöchentliches Reporting, dedizierter Onboarding-Manager.' },
    { q: 'Werden meine Daten zum Training der Modelle genutzt?', a: 'Nein. Alle Kundendaten verbleiben in isolierten Instanzen und werden niemals zum Training allgemeiner Modelle verwendet.' },
    { q: 'Wie lange dauert eine Implementierung?', a: 'Ein einfacher KI-Assistent ist in 2-4 Wochen produktiv. Komplexere CRM/ERP-Integrationen benötigen 6-12 Wochen.' },
    { q: 'Welche Systeme können integriert werden?', a: 'Über 50 Integrationen: SAP, HubSpot, Salesforce, Microsoft 365, Zendesk, Freshdesk, DATEV, Personio und viele mehr.' },
    { q: 'Ist NeXifyAI DSGVO-konform?', a: 'Ja. Alle KI-Agenten und Systeme sind DSGVO/AVG-konform. Datenverarbeitung erfolgt in EU-Rechenzentren. Wir bieten AVV-Verträge und Datenschutz-Folgenabschätzung.' },
    { q: 'Gibt es eine Testphase?', a: 'Ja. Wir bieten ein kostenloses Erstgespräch und eine 14-tägige Evaluierungsphase für Starter-Tarife. Enterprise-Kunden erhalten eine individuelle Proof-of-Concept-Phase.' }
  ],
  nl: [
    { q: 'Welke tarieven zijn er?', a: 'Wij bieden twee kern-tarieven: Starter AI Agenten AG (€499/maand) met 2 AI-agenten en Growth AI Agenten AG (€1.299/maand) met 10 AI-agenten.' },
    { q: 'Worden mijn gegevens gebruikt voor modeltraining?', a: 'Nee. Alle klantgegevens blijven in geïsoleerde instanties en worden nooit gebruikt voor algemene modeltraining.' },
    { q: 'Hoe lang duurt een implementatie?', a: 'Een eenvoudige AI-assistent is in 2-4 week productief. Complexere CRM/ERP-integraties nemen 6-12 weken in beslag.' },
    { q: 'Is NeXifyAI AVG-conform?', a: 'Ja. Alle AI-agenten en systemen zijn AVG-conform. Gegevensverwerking vindt plaats in EU-datacenters.' }
  ],
  en: [
    { q: 'What plans are available?', a: 'We offer two core plans: Starter AI Agent AG (€499/month) with 2 AI agents and Growth AI Agent AG (€1,299/month) with 10 AI agents.' },
    { q: 'Is my data used for model training?', a: 'No. All customer data remains in isolated instances and is never used for general model training.' },
    { q: 'How long does implementation take?', a: 'A simple AI assistant is productive in 2-4 weeks. Complex CRM/ERP integrations require 6-12 weeks.' },
    { q: 'Is NeXifyAI GDPR-compliant?', a: 'Yes. All AI agents and systems are GDPR-compliant. Data processing happens in EU data centers. DPA contracts available.' }
  ]
};

const L10N_ADDR = {
  nl: { streetAddress: 'Graaf van Loonstraat 1E', addressLocality: 'Venlo', postalCode: '5921 JA', addressCountry: 'NL' }
};

export default function SEOHead({ lang = 'de', page = 'home' }) {
  const m = META[lang] || META.en;
  const langTag = LANG_MAP[lang] || 'en-GB';
  const canonical = `${BASE_URL}/${lang}`;
  const breadcrumb = BREADCRUMBS[page] ? BREADCRUMBS[page](lang) : BREADCRUMBS.home(lang);
  const faqs = FAQ_DATA[lang] || FAQ_DATA.de;

  /* ─── Organization + LocalBusiness ─── */
  const orgSchema = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: "neXify - Chat it. Automat it.",
    alternateName: 'NeXifyAI',
    url: BASE_URL,
    logo: `${BASE_URL}/icon-mark.svg`,
    description: m.description,
    address: { '@type': 'PostalAddress', streetAddress: L10N_ADDR.nl.streetAddress, addressLocality: L10N_ADDR.nl.addressLocality, postalCode: L10N_ADDR.nl.postalCode, addressCountry: L10N_ADDR.nl.addressCountry },
    contactPoint: [
      { '@type': 'ContactPoint', telephone: '+31-6-133-188-56', contactType: 'sales', availableLanguage: ['German', 'Dutch', 'English'] },
      { '@type': 'ContactPoint', email: 'support@nexify-automate.com', contactType: 'support', availableLanguage: ['German', 'Dutch', 'English'] }
    ],
    sameAs: [
      'https://wa.me/31613318856'
    ]
  };

  /* ─── LocalBusiness (full details for local SEO) ─── */
  const localSchema = {
    '@context': 'https://schema.org',
    '@type': 'LocalBusiness',
    '@id': `${BASE_URL}/#business`,
    name: 'neXify - Chat it. Automat it.',
    url: BASE_URL,
    telephone: '+31-6-133-188-56',
    email: 'support@nexify-automate.com',
    address: { '@type': 'PostalAddress', streetAddress: L10N_ADDR.nl.streetAddress, addressLocality: L10N_ADDR.nl.addressLocality, postalCode: L10N_ADDR.nl.postalCode, addressCountry: L10N_ADDR.nl.addressCountry },
    areaServed: ['DE', 'AT', 'CH', 'NL', 'BE', 'EU'],
    priceRange: '€€€',
    currenciesAccepted: 'EUR',
    paymentAccepted: ['Bank Transfer', 'Credit Card', 'SEPA'],
    openingHoursSpecification: [
      { '@type': 'OpeningHoursSpecification', dayOfWeek: ['Monday', 'Tuesday', 'Wednesday', 'Thursday'], opens: '09:00', closes: '17:00' },
      { '@type': 'OpeningHoursSpecification', dayOfWeek: 'Friday', opens: '09:00', closes: '15:00' }
    ]
  };

  /* ─── WebSite ─── */
  const webSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'NeXifyAI',
    url: BASE_URL,
    potentialAction: { '@type': 'SearchAction', target: `${BASE_URL}/search?q={search_term_string}`, 'query-input': 'required name=search_term_string' }
  };

  /* ─── Service + Offers ─── */
  const serviceSchema = {
    '@context': 'https://schema.org',
    '@type': 'Service',
    serviceType: 'AI Agent Development & Enterprise Automation',
    provider: { '@type': 'Organization', name: "neXify - Chat it. Automat it." },
    areaServed: ['DE', 'AT', 'CH', 'NL', 'EU'],
    hasOfferCatalog: {
      '@type': 'OfferCatalog',
      name: 'AI Agent Packages',
      itemListElement: [
        { '@type': 'Offer', name: 'Starter', price: '499', priceCurrency: 'EUR', description: '2 AI Agents, Shared Cloud, Email Support, REST API' },
        { '@type': 'Offer', name: 'Growth', price: '1299', priceCurrency: 'EUR', description: '10 AI Agents, Private Cloud, Priority Support, CRM/ERP Kit' },
        { '@type': 'Offer', name: 'Enterprise', price: '39900', priceCurrency: 'EUR', description: 'Custom, Unlimited Agents, Dedicated Infrastructure' }
      ]
    }
  };

  /* ─── FAQ (all questions from translations) ─── */
  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map(f => ({
      '@type': 'Question', name: f.q,
      acceptedAnswer: { '@type': 'Answer', text: f.a }
    }))
  };

  return (
    <Helmet>
      <html lang={langTag} />
      <title>{m.title}</title>
      <meta name="description" content={m.description} />
      <meta name="keywords" content={m.keywords} />
      <meta name="robots" content="index, follow, max-image-preview:large" />
      <link rel="canonical" href={canonical} />

      {/* hreflang */}
      <link rel="alternate" hrefLang="de" href={`${BASE_URL}/de`} />
      <link rel="alternate" hrefLang="nl" href={`${BASE_URL}/nl`} />
      <link rel="alternate" hrefLang="en" href={`${BASE_URL}/en`} />
      <link rel="alternate" hrefLang="x-default" href={`${BASE_URL}/en`} />

      {/* Open Graph */}
      <meta property="og:type" content="website" />
      <meta property="og:site_name" content="NeXifyAI" />
      <meta property="og:title" content={m.title} />
      <meta property="og:description" content={m.description} />
      <meta property="og:url" content={canonical} />
      <meta property="og:locale" content={langTag.replace('-', '_')} />
      <meta property="og:image" content={`${BASE_URL}/og-image.png`} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />

      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={m.title} />
      <meta name="twitter:description" content={m.description} />

      {/* JSON-LD: BreadcrumbList (ALL pages) */}
      <script type="application/ld+json">{JSON.stringify(breadcrumb)}</script>

      {/* JSON-LD: Organization + LocalBusiness (homepage) */}
      {page === 'home' && <script type="application/ld+json">{JSON.stringify(orgSchema)}</script>}
      {page === 'home' && <script type="application/ld+json">{JSON.stringify(localSchema)}</script>}
      {page === 'home' && <script type="application/ld+json">{JSON.stringify(webSchema)}</script>}
      {page === 'home' && <script type="application/ld+json">{JSON.stringify(serviceSchema)}</script>}

      {/* JSON-LD: FAQPage (ALL pages — Google shows FAQs per domain, not per page) */}
      <script type="application/ld+json">{JSON.stringify(faqSchema)}</script>
    </Helmet>
  );
}
