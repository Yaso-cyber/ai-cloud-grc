const LEVEL_COLORS = {
  CRITICAL: 'text-red-400',
  HIGH: 'text-orange-400',
  MEDIUM: 'text-yellow-400',
  LOW: 'text-green-400',
}

export default function RiskScore({ risk }) {
  const color = LEVEL_COLORS[risk.level] || 'text-gray-300'
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 flex flex-col items-center justify-center gap-2">
      <p className="text-xs uppercase tracking-widest text-gray-500">Risk Score</p>
      <p className={`text-6xl font-bold ${color}`}>{risk.score}</p>
      <p className={`text-sm font-semibold ${color}`}>{risk.level}</p>
      <div className="mt-3 text-xs text-gray-400 space-y-1 w-full">
        {Object.entries(risk.breakdown || {}).map(([sev, count]) => (
          <div key={sev} className="flex justify-between">
            <span className={LEVEL_COLORS[sev] || ''}>{sev}</span>
            <span>{count}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
