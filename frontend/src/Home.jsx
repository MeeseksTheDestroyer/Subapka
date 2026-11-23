import { useEffect, useState } from 'react'

const PER_MONTH = { weekly: 52 / 12, monthly: 1, yearly: 1 / 12 }

const emptyForm = { name: '', price: '', currency: 'PLN', type: 'monthly', renewal_date: '' }

function Home({ user, onLogout }) {
  const [subs, setSubs] = useState([])
  const [types, setTypes] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [error, setError] = useState('')

  function loadSubs() {
    fetch(`/api/subscriptions?user_id=${user.id}`)
      .then((res) => res.json())
      .then((data) => setSubs(data.items))
  }

  useEffect(() => {
    loadSubs()
    fetch('/api/types')
      .then((res) => res.json())
      .then((data) => setTypes(data.items))
  }, [user.id])

  const totals = {}
  for (const s of subs) {
    if (s.status !== 'active') continue
    const monthly = Number(s.price) * (PER_MONTH[s.type] ?? 1)
    totals[s.currency] = (totals[s.currency] || 0) + monthly
  }

  function update(field) {
    return (e) => setForm({ ...form, [field]: e.target.value })
  }

  async function handleAdd(e) {
    e.preventDefault()
    setError('')
    const res = await fetch('/api/subscriptions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...form, user_id: user.id }),
    })
    if (!res.ok) {
      const data = await res.json()
      setError(Array.isArray(data.detail)
        ? data.detail.map((d) => d.msg).join(', ')
        : data.detail || 'Nie udało się dodać')
      return
    }
    setForm(emptyForm)
    loadSubs()
  }

  async function handleCancel(id) {
    await fetch(`/api/subscriptions/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'cancelled' }),
    })
    loadSubs()
  }

  async function handleDelete(id) {
    if (!window.confirm('Usunąć tę subskrypcję?')) return
    await fetch(`/api/subscriptions/${id}`, { method: 'DELETE' })
    loadSubs()
  }

  return (
    <div className="page">
      <header>
        <span>Cześć, {user.name}</span>
        <button className="link" onClick={onLogout}>Wyloguj</button>
      </header>

      <h1>Twoje subskrypcje</h1>

      {subs.length === 0 ? (
        <p>Nie masz jeszcze żadnych subskrypcji.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Nazwa</th>
              <th>Cena</th>
              <th>Okres</th>
              <th>Odnowienie</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {subs.map((s) => (
              <tr key={s.id}>
                <td>{s.name}</td>
                <td>{Number(s.price).toFixed(2)} {s.currency}</td>
                <td>{types.find((t) => t.name === s.type)?.label ?? s.type}</td>
                <td>{s.renewal_date}</td>
                <td>{s.status === 'active' ? 'aktywna' : 'anulowana'}</td>
                <td className="actions">
                  {s.status === 'active' && (
                    <button className="link" onClick={() => handleCancel(s.id)}>Anuluj</button>
                  )}
                  <button className="link" onClick={() => handleDelete(s.id)}>Usuń</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {Object.keys(totals).length > 0 && (
        <p className="total">
          Miesięcznie:{' '}
          {Object.entries(totals)
            .map(([cur, sum]) => `${sum.toFixed(2)} ${cur}`)
            .join(' + ')}
        </p>
      )}

      <h2>Dodaj subskrypcję</h2>
      <form className="row" onSubmit={handleAdd}>
        <input placeholder="Nazwa" value={form.name} onChange={update('name')} required />
        <input type="number" step="0.01" min="0.01" placeholder="Cena" value={form.price} onChange={update('price')} required />
        <input placeholder="Waluta" minLength="3" maxLength="3" value={form.currency} onChange={update('currency')} required />
        <select value={form.type} onChange={update('type')}>
          {types.map((t) => (
            <option key={t.name} value={t.name}>{t.label}</option>
          ))}
        </select>
        <input type="date" value={form.renewal_date} onChange={update('renewal_date')} required />
        <button type="submit">Dodaj</button>
      </form>
      {error && <p className="error">{error}</p>}
    </div>
  )
}

export default Home
