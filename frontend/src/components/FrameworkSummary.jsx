export default function FrameworkSummary({ summary }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 h-full">
      <h2 className="font-semibold mb-4">Failing Controls by Framework</h2>
      <div className="space-y-3">
        {Object.entries(summary || {}).map(([fw, controls]) => (
          <div key={fw}>
            <p className="text-xs font-semibold text-indigo-400 mb-1">{fw}</p>
            <div className="flex flex-wrap gap-2">
              {controls.map((ctrl) => (
                <span key={ctrl} className="px-2 py-0.5 rounded bg-indigo-900/50 text-indigo-300 text-xs font-mono">
                  {ctrl}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
