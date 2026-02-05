# 🚀 **Manifest v2.0**

A Modern Reconnaissance Framework with Rich UI, Hybrid DNS Engine & Advanced Filtering

```
███╗   ███╗ █████╗ ███╗   ██╗██╗███████╗███████╗███████╗████████╗
████╗ ████║██╔══██╗████╗  ██║██║██╔════╝██╔════╝██╔════╝╚══██╔══╝
██╔████╔██║███████║██╔██╗ ██║██║█████╗  █████╗  ███████╗   ██║
██║╚██╔╝██║██╔══██║██║╚██╗██║██║██╔══╝  ██╔══╝  ╚════██║   ██║
██║ ╚═╝ ██║██║  ██║██║ ╚████║██║███████╗██║     ███████║   ██║
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚══════╝╚═╝     ╚══════╝   ╚═╝
```

Manifest is a powerful reconnaissance tool designed for **bug bounty hunters**, **red teams**, and **security researchers**.
It delivers fast, accurate, and filtered asset discovery using a blend of **passive intelligence**, **bruteforce**, **mutations**, **DNS resolution**, and **takeover detection**.

---

# ✨ **Features**

## 🔍 Passive Enumeration (Free & API-less)

Collects subdomains from **15+ public intelligence sources**, such as:

* crt.sh
* HackerTarget
* AlienVault
* URLScan
* ThreatCrowd
* Riddler
* Wayback Machine
* RapidDNS
* Anubis
* BufferOver
* CertSpotter
  …and many more.

Runs fully asynchronous → extremely fast.

---

## ⚡ Active Discovery

### 🔨 Bruteforce Engine

* Uses custom wordlists
* Multi-threaded & optimized
* Auto-deduplication

### 🔁 Permutation Engine (DNSTwist-like)

Generates:

* Hyphen swaps
* Repeated characters
* Prefix/suffix additions
* Numeric variations
* TLD variants

---

## 🌐 DNS Resolution Engine

* Async resolver for IPv4/IPv6
* Optional **MassDNS** integration
* Wildcard detection
* Supports:

```
--resolve-dns
--resolved-only
--dns-timeout
--max-resolve
```

---

## 🛡️ Takeover Detection

Identifies vulnerable **CNAME chains** across:

* GitHub Pages
* AWS S3
* Azure
* Cloudflare Pages
* Heroku
* Netlify
* Render
* Firebase
* ReadTheDocs
* Pantheon
  …and more.

Includes concurrency controls and progress indicators.

---

## 🧠 Smart Filtering Engine

Levels:

* `none` — raw results
* `light` — basic cleanup
* `normal` — default balanced cleanup
* `aggressive` — high-value assets only
* `intelligent` — heuristic ranking

Supports:

* Noise removal
* Wildcard trimming
* Subdomain profiling
* Categorization (admin/API/dev/CDN)

---

## 🖥 Rich Terminal UI (Powered by Rich)

* Premium ASCII banner
* Color-coded logs
* Progress bars
* Tables & summaries
* Highlighted critical findings

---

## 📊 Reporting System

### 📄 **HTML Dashboard (TailwindCSS + Charts.js)**

Contains:

* Subdomain list
* IP resolution
* Takeover findings
* Statistics & charts
* Filter stats
* Clean, dark-themed design

### 📦 JSON Output

Structured, machine-readable for automation.

### 📝 TXT Export

Subdomain-only list for tools like:

```
httpx
nuclei
naabu
katana
```

---

# 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/samsatwork7/Manifest.git
cd Manifest
```

### 2. Setup Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Requirements

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

---

# 💻 Usage

## Basic Commands

| Action                | Command                                       |
| --------------------- | --------------------------------------------- |
| Show help             | `manifest -h`                                 |
| Passive only          | `manifest -d example.com --passive`           |
| Full recon            | `manifest -d example.com --all`               |
| Bruteforce            | `manifest -d example.com --brute -w list.txt` |
| Generate permutations | `manifest -d example.com --perms`             |

---

## DNS Mode

```bash
manifest -d example.com --resolve-dns
manifest -d example.com --resolved-only
```

## Filtering

```bash
manifest -d example.com --filter intelligent
manifest -d example.com --filter aggressive
```

## Reporting

```bash
manifest -d example.com --html --json --txt --output reports/
```

## Performance

```bash
manifest -d example.com --threads 500
```

---

# 📊 Example Output

### Terminal Summary

```
[+] Passive: 142 found
[+] Bruteforce: 38 found
[+] Permutations: 120 generated
[+] Filtered: 96 removed
[✓] Final: 204 subdomains
[!] Takeovers: 2 potential risks
```

### HTML Dashboard Preview

Includes:

* Statistics
* Charts
* IP resolution
* Takeover detection
* Searchable tables
* Modern UI

---

# 🗺 Roadmap

### 📌 v2.1

* HTTP probing (status, title)
* Favicon hashing
* Tech stack detection

### 📌 v2.2

* JS extraction
* API key pattern detection
* Automated wordlist builder

### 📌 v3.0

* Multi-target parallel scanning
* Nuclei integration
* Complete asset inventory

---

# 📝 License

Licensed under **MIT License** — fully open for modification and distribution.

---

# 👤 Author

**Satyam Singh**
GitHub: [@samsatwork7](https://github.com/samsatwork7)

---

# 🤝 Contributions

Contributions and feature requests are welcome!
Open an issue before large features.

---

# 🎯 Ethical Notice

Manifest is intended for **authorized** testing and educational purposes only.
Unauthorized scanning is illegal.
