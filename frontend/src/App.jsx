import { useState, useEffect } from 'react'
import RiskScore from './components/RiskScore'
import FindingsTable from './components/FindingsTable'
import FrameworkSummary from './components/FrameworkSummary'
import ExportButton from './components/ExportButton'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL || '/api'

export default function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchScan = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await axios.get(`${API}/scan`)
      setData(res.data)
    } catch (e) {
      setError('Failed to reach the backend. Is the API running?')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchScan() }, [])

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight">ai-cloud-grc</h1>
          <p className="text-xs text-gray-400">AI-driven Cloud GRC Toolkit</p>
        </div>
        <div className="flex gap-3">
          {data && <ExportButton findings={data.findings} risk={data.risk} />}
          <button
            onClick={fetchScan}
            className="px-4 py-2 rounded bg-indigo-600 hover:bg-indigo-500 text-sm font-medium transition-colors"
          >
            Re-scan
          </button>
        </div>
      </header>

      <main className="px-6 py-8 max-w-7xl mx-auto space-y-8">
        {loading && (
          <div className="text-center text-gray-400 py-20">Running scan...</div>
        )}
        {error && (
          <div className="bg-red-900/40 border border-red-700 rounded p-4 text-red-300">{error}</div>
        )}
        {data && !loading && (
          <>
            {/* Risk score + framework summary row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <RiskScore risk={data.risk} />
              <div className="md:col-span-2">
                <FrameworkSummary summary={data.framework_summary} />
              </div>
            </div>

            {/* Findings table */}
            <FindingsTable findings={data.findings} />
          </>
        )}
      </main>
    </div>
  )
}
