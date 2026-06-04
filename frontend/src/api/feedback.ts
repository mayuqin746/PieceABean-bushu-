import api from './index'

export interface SuggestionForm {
  title: string
  content: string
  contact?: string
}

export async function submitSuggestion(data: SuggestionForm) {
  const { data: result } = await api.post('/suggestions/', data)
  return result
}

export type FeedbackType = 'bug' | 'suggestion' | 'other'

export interface FeedbackForm {
  type: FeedbackType
  content: string
  contact?: string
}

export async function submitFeedback(data: FeedbackForm) {
  const { data: result } = await api.post('/feedbacks/', data)
  return result
}

export interface FAQItem {
  id: number
  question: string
  answer: string
  sort_order: number
  is_visible: boolean
  created_at: string
}

export async function fetchFaqs(): Promise<FAQItem[]> {
  const { data } = await api.get<FAQItem[]>('/faqs/')
  return data
}
