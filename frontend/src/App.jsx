import { useState } from 'react'
import Login from './Login.jsx'
import Home from './Home.jsx'
import './App.css'
 
function loadUser() {
  try {
    return JSON.parse(localStorage.getItem('user'))
  } catch {
    return null
  }
}
 
function App() {
  const [user, setUser] = useState(loadUser)
 
  function handleLogin(u) {
    localStorage.setItem('user', JSON.stringify(u))
    setUser(u)
  }
 
  function handleLogout() {
    localStorage.removeItem('user')
    setUser(null)
  }
 
  return user
    ? <Home user={user} onLogout={handleLogout} />
    : <Login onLogin={handleLogin} />
}
 
export default App
