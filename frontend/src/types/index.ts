// Re-export all types from api module for convenience
export * from '../api'

// Additional shared types that aren't in api.ts
export interface ChartTheme {
  primary: string
  secondary: string
  background: string
  text: string
  accent: string
}

export interface APIError {
  message: string
  code?: string
}

export interface Pagination {
  page: number
  pageSize: number
  total: number
  totalPages: number
}
