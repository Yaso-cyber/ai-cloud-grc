const SEVERITY_BADGE = {
  CRITICAL: 'bg-red-900 text-red-300',
  HIGH: 'bg-orange-900 text-orange-300',
  MEDIUM: 'bg-yellow-900 text-yellow-300',
  LOW: 'bg-green-900 text-green-300',
  INFO: 'bg-gray-700 text-gray-300',
}

export default function FindingsTable({ findings }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-800">
        <h2 className="font-semibold">Findings ({findings.length})</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs text-gray-500 uppercase tracking-wide border-b border-gray-800">
              <th className="px-6 py-3 text-left">Severity</th>
              <th className="px-6 py-3 text-left">Control</th>
              <th className="px-6 py-3 text-left">Resource</th>
              <th className="px-6 py-3 text-left">Description</th>
              <th className="px-6 py-3 text-left">Frameworks</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {findings.map((f) => (
              <tr key={f.id} className="hover:bg-gray-800/50 transition-colors">
                <td className="px-6 py-3">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${SEVERITY_BADGE[f.severity] || SEVERITY_BADGE.INFO}`}>
                    {f.severity}
                  </span>
                </td>
                <td className="px-6 py-3 font-mono text-xs text-indigo-300">{f.control_id}</td>
                <td className="px-6 py-3 font-mono text-xs text-gray-300">{f.resource_id}</td>
                <td className="px-6 py-3 text-gray-200 max-w-xs">{f.description}</td>
                <td className="px-6 py-3 text-xs text-gray-400">
                  {Object.entries(f.framework_refs || {}).map(([fw, ctrls]) => (
                    <div key={fw}>
                      <span className="text-indigo-400">{fw}</span>: {ctrls.join(', ')}
                    </div>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
