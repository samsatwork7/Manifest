# 🚀 Manifest v1.0

### A Modern Reconnaissance Framework with Rich UI + Hybrid DNS Engine

```text
███╗   ███╗ █████╗ ███╗   ██╗██╗███████╗███████╗███████╗████████╗
████╗ ████║██╔══██╗████╗  ██║██║██╔════╝██╔════╝██╔════╝╚══██╔══╝
██╔████╔██║███████║██╔██╗ ██║██║█████╗  █████╗  ███████╗   ██║   
██║╚██╔╝██║██╔══██║██║╚██╗██║██║██╔══╝  ██╔══╝  ╚════██║   ██║   
██║ ╚═╝ ██║██║  ██║██║ ╚████║██║███████╗██║     ███████║   ██║   
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚══════╝╚═╝     ╚══════╝   ╚═╝   

```

**Manifest** is a next-generation reconnaissance tool designed for speed, simplicity, and actionable intelligence. It combines passive data mining with high-performance active discovery.

---

## ✨ Features

* **Free Passive Enumeration:** No API keys required. Scrapes `crt.sh`, `HackerTarget`, `AlienVault`, `URLScan`, and more.
* **Bruteforce Engine:** High-speed subdomain discovery using customizable wordlists.
* **Permutations (DNSTwist-style):** Smart generation of mutations (hyphens, number flips, common prefixes/suffixes).
* **Hybrid DNS Engine:** * Automatically detects and uses **MassDNS** if available.
* Falls back to a high-concurrency **Async Resolver**.
* Full support for IPv4 and IPv6.


* **Wildcard Detection:** Intelligent filtering to eliminate false positives.
* **Takeover Detection:** Identifies CNAME vulnerabilities for GitHub, S3, Azure, Heroku, and more.
* **Rich UI & Reporting:**
* **Terminal:** Beautiful, animated, color-coded progress via Python Rich.
* **Dashboard:** Generates a TailwindCSS + Chart.js HTML report.



---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/samsatwork7/Manifest.git
cd Manifest

```

### 2. Set up Environment

```bash
python3 -m venv venv
source venv/bin/activate

```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install .

```

---

## 💻 Usage

### Basic Commands

| Goal | Command |
| --- | --- |
| **View Help** | `manifest -h` |
| **Passive Only** | `manifest -d example.com --passive` |
| **Full Recon** | `manifest -d example.com --all` |
| **Custom Wordlist** | `manifest -d example.com --brute -w list.txt` |

### Advanced Options

* **Set Threads:** `manifest -d example.com --threads 500`
* **Permutations Only:** `manifest -d example.com --perms`
* **Export HTML:** `manifest -d example.com --html --output reports/`

---

## 📊 Output Examples

### Terminal Interface

```text
[+] Passive: 142 found
[+] DNS: 36 live subdomains
[+] Wildcard filtering done
[!] 0 takeover candidates
[✓] Recon completed successfully!

```

### HTML Dashboard

The generated report provides a dark-themed, interactive overview of your target's infrastructure, including statistical breakdowns and vulnerability alerts.

---

## 🗺️ Roadmap

* [ ] **v1.1:** HTTP probing (Status/Title), Favicon hashing, and Page screenshots.
* [ ] **v1.2:** JS file extraction and API key pattern matching.
* [ ] **v2.0:** Multi-domain parallel scanning and Nuclei integration.

---

## 📝 License & Credits

* **License:** MIT License. Feel free to modify and distribute.
* **Author:** [Satyam Singh (@samsatwork7)](https://www.google.com/search?q=https://github.com/samsatwork7)
* **Contributions:** Pull requests are welcome! Please open an issue first to discuss major changes.

---

> **Note:** This tool is for educational and ethical security testing only.
