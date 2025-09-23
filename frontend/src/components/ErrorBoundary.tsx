import React from "react";

interface ErrorBoundaryProps {
  fallback?: React.ReactNode; // what to render when error happens
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    // ✅ Update state so next render shows fallback
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // ✅ You can log errors to monitoring service (Sentry, LogRocket, etc.)
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="p-4 bg-red-100 text-red-700 rounded-md">
            <h2>⚠️ Something went wrong.</h2>
            <pre>{this.state.error?.message}</pre>
          </div>
        )
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
