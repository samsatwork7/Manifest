import json
import os

class HTMLReport:

    TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Manifest v1.0 Report — {domain}</title>

<!-- TailwindCSS -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body {{
  background-color: #0f172a;
  color: #e2e8f0;
  font-family: 'Inter', sans-serif;
}}
.card {{
  background-color: #1e293b;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}}
.heading {{
  font-size: 1.5rem;
  margin-bottom: 12px;
  font-weight: 600;
}}
.badge {{
  padding: 4px 10px;
  border-radius: 8px;
  background-color: #334155;
}}
</style>

</head>
<body class="p-6">

<h1 class="text-4xl font-bold mb-6 text-cyan-400">Manifest v1.0 — Recon Report</h1>
<h2 class="text-xl mb-8">Target: {domain}</h2>

<div class="grid grid-cols-1 md:grid-cols-2 gap-6">

  <div class="card">
    <div class="heading">Summary</div>
    <p><b>Total Subdomains:</b> {total_subs}</p>
    <p><b>Takeover Candidates:</b> {total_takeovers}</p>
  </div>

  <div class="card">
    <div class="heading">Subdomain Distribution</div>
    <canvas id="chart1"></canvas>
  </div>

</div>

<div class="card mt-6">
  <div class="heading">Subdomains</div>
  <table class="table-auto w-full">
    <thead>
      <tr>
        <th class="px-4 py-2 text-left">Subdomain</th>
        <th class="px-4 py-2 text-left">IPv4</th>
        <th class="px-4 py-2 text-left">IPv6</th>
      </tr>
    </thead>
    <tbody>
      {subdomain_rows}
    </tbody>
  </table>
</div>

<div class="card mt-6">
  <div class="heading">Takeover Candidates</div>
  {takeover_section}
</div>

<script>
new Chart(document.getElementById("chart1"), {{
    type: "pie",
    data: {{
        labels: ["Live Subdomains", "Takeover Risk"],
        datasets: [{{
            data: [{total_subs}, {total_takeovers}],
            backgroundColor: ["#0ea5e9", "#ef4444"]
        }}]
    }}
}});
</script>

</body>
</html>
"""

    @staticmethod
    def build_row(sd):
        return f"""
<tr>
  <td class="px-4 py-2">{sd['subdomain']}</td>
  <td class="px-4 py-2">{", ".join(sd.get("ipv4", []))}</td>
  <td class="px-4 py-2">{", ".join(sd.get("ipv6", []))}</td>
</tr>
"""

    @staticmethod
    def build_takeover(t):
        return f"""
<div class="p-3 mb-2 bg-red-700 rounded">
  <p><b>{t['subdomain']}</b></p>
  <p>CNAME: {t.get('cname','N/A')}</p>
</div>
"""

    @staticmethod
    def write(filepath, domain, subdomains, takeovers):
        rows = "\n".join(HTMLReport.build_row(s) for s in subdomains)

        takeover_html = (
            "\n".join(HTMLReport.build_takeover(t) for t in takeovers)
            if takeovers else "<p>No takeovers detected.</p>"
        )

        html = HTMLReport.TEMPLATE.format(
            domain=domain,
            total_subs=len(subdomains),
            total_takeovers=len(takeovers),
            subdomain_rows=rows,
            takeover_section=takeover_html
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
