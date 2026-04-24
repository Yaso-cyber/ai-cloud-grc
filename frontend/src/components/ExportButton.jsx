import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

export default function ExportButton({ findings, risk }) {
  const handleExport = () => {
    const doc = new jsPDF({ orientation: 'landscape' })

    doc.setFontSize(18)
    doc.text('Cloud GRC Compliance Report', 14, 18)
    doc.setFontSize(10)
    doc.text(`Generated: ${new Date().toISOString()}`, 14, 26)
    doc.text(`Risk Score: ${risk.score}/100 (${risk.level})`, 14, 32)

    autoTable(doc, {
      startY: 38,
      head: [['Severity', 'Control', 'Resource', 'Description', 'Remediation']],
      body: findings.map((f) => [
        f.severity,
        f.control_id,
        f.resource_id,
        f.description,
        f.remediation_hint || '',
      ]),
      styles: { fontSize: 8 },
      headStyles: { fillColor: [79, 70, 229] },
    })

    doc.save('grc-report.pdf')
  }

  return (
    <button
      onClick={handleExport}
      className="px-4 py-2 rounded bg-gray-700 hover:bg-gray-600 text-sm font-medium transition-colors"
    >
      Export PDF
    </button>
  )
}
