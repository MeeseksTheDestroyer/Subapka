import { useState } from 'react'

function post(url, body) {
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

async function errorText(res) {
  const data = await res.json()
  if (typeof data.detail === 'string') return data.detail
  if (Array.isArray(data.detail)) return data.detail.map((d) => d.msg).join(', ')
  return 'Coś poszło nie tak'
}

function Login({ onLogin }) {
  const [mode, setMode] = useState('login')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const isLogin = mode === 'login'

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (!isLogin) {
      const res = await post('/api/users', { name, email, password })
      if (!res.ok) {
        setError(await errorText(res))
        return
      }
    }

    const res = await post('/api/users/login', { email, password })
    if (!res.ok) {
      setError(await errorText(res))
      return
    }
    const data = await res.json()
    onLogin(data.user)
  }

  return (
    <div className="page narrow">
      <h1>Subapka</h1>
      <h2>{isLogin ? 'Logowanie' : 'Rejestracja'}</h2>

      <form onSubmit={handleSubmit}>
        {!isLogin && (
          <label>
            Nazwa
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </label>
        )}
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Hasło
          <input type="password" minLength={isLogin ? undefined : 8} value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>

        {error && <p className="error">{error}</p>}

        <button type="submit">{isLogin ? 'Zaloguj' : 'Załóż konto'}</button>
      </form>

      <p>
        {isLogin ? 'Nie masz konta? ' : 'Masz już konto? '}
        <button className="link" onClick={() => setMode(isLogin ? 'register' : 'login')}>
          {isLogin ? 'Zarejestruj się' : 'Zaloguj się'}
        </button>
      </p>
    </div>
  )
}

export default Login
