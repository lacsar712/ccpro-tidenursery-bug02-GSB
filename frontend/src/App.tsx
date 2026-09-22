import type { ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { getToken } from './api/client'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Hatcheries from './pages/Hatcheries'
import Ponds from './pages/Ponds'
import WaterSamples from './pages/WaterSamples'
import FeedEvents from './pages/FeedEvents'

function PrivateRoute({ children }: { children: ReactNode }) {
  if (!getToken()) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="hatcheries" element={<Hatcheries />} />
        <Route path="ponds" element={<Ponds />} />
        <Route path="water-samples" element={<WaterSamples />} />
        <Route path="feed-events" element={<FeedEvents />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
