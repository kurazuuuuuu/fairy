const TOKEN_KEY = 'fairy_jwt_token'
const USER_ID_KEY = 'fairy_user_id'

export async function getToken(): Promise<string> {
  let token = localStorage.getItem(TOKEN_KEY)
  
  if (!token) {
    token = await generateToken()
  }
  
  return token
}

async function generateToken(): Promise<string> {
  const userId = getUserId()
  const apiUrl = (window as any).ENV?.VITE_API_URL || import.meta.env.VITE_API_URL || ''
  
  const response = await fetch(`${apiUrl}/api/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId })
  })
  
  if (!response.ok) {
    throw new Error('Failed to generate token')
  }
  
  const data = await response.json()
  localStorage.setItem(TOKEN_KEY, data.access_token)
  
  return data.access_token
}

function getUserId(): number {
  let userId = localStorage.getItem(USER_ID_KEY)
  
  if (!userId) {
    userId = Math.floor(Math.random() * 1000000).toString()
    localStorage.setItem(USER_ID_KEY, userId)
  }
  
  return parseInt(userId)
}

export async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
  const token = await getToken()
  
  const headers: Record<string, string> = {
    'Authorization': `Bearer ${token}`
  }
  
  if (options.headers) {
    Object.assign(headers, options.headers)
  }
  
  const response = await fetch(url, { ...options, headers })
  
  if (response.status === 401) {
    localStorage.removeItem(TOKEN_KEY)
    const newToken = await generateToken()
    headers['Authorization'] = `Bearer ${newToken}`
    return fetch(url, { ...options, headers })
  }
  
  return response
}
