import { FormEvent, useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Hatchery } from '../types'

const empty = { name: '', seawaterSource: '', notes: '' }

export default function Hatcheries() {
  const [rows, setRows] = useState<Hatchery[]>([])
  const [form, setForm] = useState(empty)
  const [error, setError] = useState('')

  async function load() {
    const data = await api<Hatchery[]>('/api/hatcheries')
    setRows(data)
  }

  useEffect(() => {
    load().catch((e) => setError(e.message))
  }, [])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    try {
      await api('/api/hatcheries', {
        method: 'POST',
        body: JSON.stringify(form),
      })
      setForm(empty)
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败')
    }
  }

  async function remove(id: number) {
    if (!confirm('确认删除该育苗场？')) return
    try {
      await api(`/api/hatcheries/${id}`, { method: 'DELETE' })
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除失败')
    }
  }

  return (
    <div>
      <header className="page-header">
        <h1>育苗场</h1>
        <p className="muted">登记海水来源与场区备注</p>
      </header>
      {error && <div className="error">{error}</div>}

      <form className="panel form-grid" onSubmit={onSubmit}>
        <label>
          名称
          <input
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
        </label>
        <label>
          海水来源
          <input
            value={form.seawaterSource}
            onChange={(e) => setForm({ ...form, seawaterSource: e.target.value })}
            required
          />
        </label>
        <label className="span-2">
          备注
          <input
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
          />
        </label>
        <button type="submit" className="btn primary">
          新增育苗场
        </button>
      </form>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>名称</th>
              <th>海水来源</th>
              <th>备注</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{r.name}</td>
                <td>{r.seawaterSource}</td>
                <td>{r.notes || '—'}</td>
                <td>
                  <button className="btn ghost" onClick={() => remove(r.id)}>
                    删除
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
