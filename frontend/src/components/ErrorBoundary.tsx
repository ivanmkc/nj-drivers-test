import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

/**
 * Last line of defence: without this, any render-time throw leaves the user
 * with a blank white page. Copy is hard-coded English because the i18n
 * strings may be the thing that failed to load.
 */
export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Unhandled render error', error, info.componentStack);
  }

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center" role="alert">
        <div className="text-error text-lg font-semibold mb-2">Something went wrong</div>
        <div className="text-muted text-sm mb-6 break-words">{this.state.error.message}</div>
        <button
          onClick={() => window.location.reload()}
          className="px-6 py-2 bg-primary text-on-primary rounded-xl text-sm font-semibold cursor-pointer hover:bg-primary-hover transition-colors"
        >
          Reload
        </button>
      </div>
    );
  }
}
