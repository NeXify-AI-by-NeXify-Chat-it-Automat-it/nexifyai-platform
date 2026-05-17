import React from 'react';
import { getCapturedErrors } from '../observability/frontend/runtime_error_capture';

class EnhancedErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    
    const runtimeErrors = getCapturedErrors();
    const isDev = process.env.NODE_ENV === 'development' || 
                  window.location.hostname.includes('vercel.app');
    
    if (isDev) {
      console.group('\u{1F534} NeXifyAI Runtime Error');
      console.error('Error:', error);
      console.error('Component Stack:', errorInfo.componentStack);
      console.error('Runtime Errors:', runtimeErrors);
      console.error('Route:', window.location.pathname);
      console.groupEnd();
    }
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      const isDev = process.env.NODE_ENV === 'development' || 
                    window.location.hostname.includes('vercel.app');

      if (!isDev) {
        return (
          <div style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            minHeight: '100vh', fontFamily: 'system-ui, sans-serif', padding: '2rem', textAlign: 'center',
            background: '#0d1117', color: '#c9d1d9'
          }}>
            <h1 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#f85149' }}>
              {'\u26A1'} Etwas ist schiefgelaufen
            </h1>
            <p style={{ marginBottom: '1.5rem', color: '#8b949e' }}>
              Ein unerwarteter Fehler ist aufgetreten. Bitte laden Sie die Seite neu.
            </p>
            <button onClick={() => window.location.reload()} style={{
              padding: '0.75rem 2rem', background: '#238636', color: '#fff', border: 'none',
              borderRadius: '6px', cursor: 'pointer', fontSize: '1rem'
            }}>
              Seite neu laden
            </button>
          </div>
        );
      }

      const runtimeErrors = getCapturedErrors();

      return (
        <div style={{
          fontFamily: 'system-ui, sans-serif', padding: '2rem', background: '#0d1117',
          color: '#c9d1d9', minHeight: '100vh'
        }}>
          <h1 style={{ color: '#f85149', borderBottom: '1px solid #30363d', paddingBottom: '0.5rem' }}>
            {'\u{1F534}'} Runtime Error Diagnostics (Preview Mode)
          </h1>

          <h2 style={{ color: '#f0883e', marginTop: '1.5rem' }}>Error</h2>
          <pre style={{ background: '#161b22', padding: '1rem', borderRadius: '6px', overflow: 'auto', fontSize: '0.9rem' }}>
            {this.state.error?.message}
          </pre>

          <h2 style={{ color: '#f0883e', marginTop: '1.5rem' }}>Stack Trace</h2>
          <pre style={{ background: '#161b22', padding: '1rem', borderRadius: '6px', overflow: 'auto', fontSize: '0.85rem', maxHeight: '400px' }}>
            {this.state.error?.stack}
          </pre>

          {this.state.errorInfo?.componentStack && (
            <>
              <h2 style={{ color: '#f0883e', marginTop: '1.5rem' }}>Component Stack</h2>
              <pre style={{ background: '#161b22', padding: '1rem', borderRadius: '6px', overflow: 'auto', fontSize: '0.85rem' }}>
                {this.state.errorInfo.componentStack}
              </pre>
            </>
          )}

          <h2 style={{ color: '#f0883e', marginTop: '1.5rem' }}>Route</h2>
          <pre style={{ background: '#161b22', padding: '0.5rem 1rem', borderRadius: '6px' }}>
            {window.location.pathname}
          </pre>

          {runtimeErrors.length > 0 && (
            <>
              <h2 style={{ color: '#f0883e', marginTop: '1.5rem' }}>Captured Runtime Errors ({runtimeErrors.length})</h2>
              {runtimeErrors.map((e, i) => (
                <pre key={i} style={{ background: '#161b22', padding: '0.5rem 1rem', borderRadius: '6px', marginBottom: '0.5rem', fontSize: '0.85rem' }}>
                  <strong>[{e.type}]</strong> {e.message}{'\n'}{e.stack && e.stack.slice(0, 300)}
                </pre>
              ))}
            </>
          )}

          <button onClick={() => window.location.reload()} style={{
            marginTop: '2rem', padding: '0.75rem 2rem', background: '#238636', color: '#fff',
            border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '1rem'
          }}>
            Seite neu laden
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default EnhancedErrorBoundary;
