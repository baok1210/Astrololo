import { Component } from 'react'

class ErrorBoundary extends Component<{ children: React.ReactNode }, { hasError: boolean; error: Error | null }> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('React Error Boundary caught an error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ 
          padding: 40, 
          textAlign: 'center', 
          background: '#fff', 
          borderRadius: 8, 
          margin: '20px auto', 
          maxWidth: 600, 
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ color: '#d9534f', marginTop: 0 }}>Đã có lỗi xảy ra</h2>
          <p style={{ color: '#555', marginBottom: 20 }}>
            Ứng dụng gặp sự cố. Vui lòng tải lại trang.
          </p>
          <details style={{ 
            textAlign: 'left', 
            background: '#f8f9fa', 
            padding: 16, 
            borderRadius: 4, 
            fontSize: 12
          }}>
            <summary style={{ cursor: 'pointer', color: '#6b3a3a' }}>Chi tiết lỗi</summary>
            <pre style={{ marginTop: 8, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
              {this.state.error?.message}
            </pre>
          </details>
          <button
            onClick={() => window.location.reload()}
            style={{ marginTop: 20, padding: '10px 20px', background: '#6b3a3a', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer', fontSize: 14 }}
          >
            Tải lại trang
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
