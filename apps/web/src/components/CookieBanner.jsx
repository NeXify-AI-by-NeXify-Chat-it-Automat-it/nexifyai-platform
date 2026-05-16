import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const CookieBanner = () => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const accepted = localStorage.getItem('cookie_accepted');
    if (!accepted) setVisible(true);
  }, []);

  const handleAccept = () => {
    localStorage.setItem('cookie_accepted', 'true');
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <motion.div
      className="cookie-banner"
      role="dialog"
      aria-label="Cookie-Hinweis"
      data-testid="cookie-banner"
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="cookie-inner">
        <div className="cookie-text">
          Diese Website verwendet keine Tracking-Cookies. Nur technisch notwendige Cookies.
        </div>
        <div className="cookie-actions">
          <button
            className="btn btn-sm btn-primary"
            onClick={handleAccept}
            data-testid="cookie-accept"
            style={{
              background: 'var(--nx-accent, #FE9B7B)',
              border: 'none',
              color: '#fff'
            }}
          >
            Verstanden
          </button>
        </div>
      </div>
    </motion.div>
  );
};

export default CookieBanner;
