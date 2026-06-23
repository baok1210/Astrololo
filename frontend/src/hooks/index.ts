"use client"

import { useState, useEffect, useCallback, useRef } from 'react'
import { BirthData } from '../api'

interface UseBirthForm {
  initialData?: Partial<BirthData>
  onSubmit: (data: BirthData) => void | Promise<void>
  validate?: (data: Partial<BirthData>) => Record<string, string> | null
}

export function useBirthForm({ initialData, onSubmit, validate }: UseBirthForm) {
  const [data, setData] = useState<Partial<BirthData>>(initialData || {})
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const updateField = useCallback((field: keyof BirthData, value: any) => {
    setData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }, [errors])

  const validateForm = useCallback((): boolean => {
    if (!validate) return true

    const validationErrors = validate(data)
    if (validationErrors) {
      setErrors(validationErrors)
      return false
    }

    setErrors({})
    return true
  }, [validate, data])

  const handleSubmit = useCallback(async (e?: React.FormEvent) => {
    if (e) e.preventDefault()

    if (!validateForm()) return

    setIsSubmitting(true)
    try {
      await onSubmit(data as BirthData)
    } catch (error) {
      console.error('Form submission error:', error)
    } finally {
      setIsSubmitting(false)
    }
  }, [validateForm, onSubmit, data])

  const reset = useCallback(() => {
    setData(initialData || {})
    setErrors({})
  }, [initialData])

  return {
    data,
    errors,
    isSubmitting,
    updateField,
    handleSubmit,
    validateForm,
    reset,
  }
}

interface UseAPI<T> {
  execute: (...args: any[]) => Promise<T>
  data: T | null
  error: Error | null
  isLoading: boolean
}

export function useAPI<T>(
  apiFunction: (...args: any[]) => Promise<T>
): UseAPI<T> {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const execute = useCallback(
    async (...args: any[]) => {
      setIsLoading(true)
      setError(null)
      try {
        const result = await apiFunction(...args)
        setData(result)
        return result
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err))
        setError(error)
        throw error
      } finally {
        setIsLoading(false)
      }
    },
    [apiFunction]
  )

  return { execute, data, error, isLoading }
}
