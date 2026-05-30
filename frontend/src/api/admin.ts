import api from './index'

export async function uploadPattern(form: FormData) {
  const { data } = await api.post('/admin/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
