import { useEffect, useState } from 'react'
import heroImg from './assets/hero.png'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import './App.css'

function App() {
  const [types, setTypes] = useState([])

  useEffect(() => {
    fetch('/api/types')
      .then((res) => res.json())
      .then((data) => setTypes(data.items))
  }, [])

  return (
    <ul>
      {JSON.stringify(types)}
    </ul>
  )
}

export default App
