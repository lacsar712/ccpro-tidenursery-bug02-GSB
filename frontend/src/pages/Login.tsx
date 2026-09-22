import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, setToken } from '../api/client'

export default function Login() {
  const navigate = useNavigate()
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('123456')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await login(username, password)
      setToken(res.access_token)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-panel">
        <div className="login-wave" />
        <h1>TideNursery</h1>
        <p className="muted">海水育苗场 · 塘口水质采样与投喂事件台账</p>
        <form onSubmit={onSubmit} className="form-stack">
          <label>
            用户名
            <input value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>
          <label>
            密码
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>
          {error && <div className="error">{error}</div>}
          <button type="submit" className="btn primary" disabled={loading}>
            {loading ? '登录中…' : '进入台账'}
          </button>
        </form>
        <p className="hint">演示账号：admin / technician，密码均为 123456</p>
      </div>
    </div>
  )
}
