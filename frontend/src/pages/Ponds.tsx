import { FormEvent, useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Hatchery, Pond } from '../types'

const empty = {
  hatcheryId: 0,
  pondCode: '',
  species: '',
  volumeM3: 50,
  status: 'stocked' as Pond['status'],
}

export default function Ponds() {
  const [hatcheries, setHatcheries] = useState<Hatchery[]>([])
  const [rows, setRows] = useState<Pond[]>([])
  const [form, setForm] = useState(empty)
  const [error, setError] = useState('')

  async function load() {
    const [hs, ps] = await Promise.all([
      api<Hatchery[]>('/api/hatcheries'),
      api<Pond[]>('/api/ponds'),
    ])
    setHatcheries(hs)
    setRows(ps)
    if (!form.hatcheryId && hs[0]) {
      setForm((f) => ({ ...f, hatcheryId: hs[0].id }))
    }
  }

  useEffect(() => {
    load().catch((e) => setError(e.message))
  }, [])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    try {
      await api('/api/ponds', {
        method: 'POST',
        body: JSON.stringify(form),
      })
      setForm((f) => ({ ...empty, hatcheryId: f.hatcheryId }))
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败')
    }
  }

  async function remove(id: number) {
    if (!confirm('确认删除该塘口？')) return
    try {
      await api(`/api/ponds/${id}`, { method: 'DELETE' })
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除失败')
    }
  }

  const hatcheryName = (id: number) =>
    hatcheries.find((h) => h.id === id)?.name || `#${id}`

  return (
    <div>
      <header className="page-header">
        <h1>育苗塘</h1>
        <p className="muted">同场塘口号唯一；状态：stocked / dry / quarantine</p>
      </header>
      {error && <div className="error">{error}</div>}

      <form className="panel form-grid" onSubmit={onSubmit}>
        <label>
          所属育苗场
          <select
            value={form.hatcheryId}
            onChange={(e) => setForm({ ...form, hatcheryId: Number(e.target.value) })}
            required
          >
            {hatcheries.map((h) => (
              <option key={h.id} value={h.id}>
                {h.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          塘口号
          <input
            value={form.pondCode}
            onChange={(e) => setForm({ ...form, pondCode: e.target.value })}
            required
          />
        </label>
        <label>
          养殖品种
          <input
            value={form.species}
            onChange={(e) => setForm({ ...form, species: e.target.value })}
            required
          />
        </label>
        <label>
          水体体积 (m³)
          <input
            type="number"
            step="0.1"
            min="0.1"
            value={form.volumeM3}
            onChange={(e) => setForm({ ...form, volumeM3: Number(e.target.value) })}
            required
          />
        </label>
        <label>
          状态
          <select
            value={form.status}
            onChange={(e) =>
              setForm({ ...form, status: e.target.value as Pond['status'] })
            }
          >
            <option value="stocked">stocked 在养</option>
            <option value="dry">dry 干塘</option>
            <option value="quarantine">quarantine 隔离</option>
          </select>
        </label>
        <button type="submit" className="btn primary">
          新增塘口
        </button>
      </form>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>育苗场</th>
              <th>塘口号</th>
              <th>品种</th>
              <th>体积 m³</th>
              <th>状态</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>{r.id}</td>
                <td>{hatcheryName(r.hatcheryId)}</td>
                <td>{r.pondCode}</td>
                <td>{r.species}</td>
                <td>{r.volumeM3}</td>
                <td>
                  <span className={`badge ${r.status}`}>{r.status}</span>
                </td>
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
