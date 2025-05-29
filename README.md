# 🔐 Container Hardening Analyzer

**Container Hardening Analyzer** is a simple Python tool to find security problems in Dockerfiles and Kubernetes YAML files. It checks for common issues and shows suggestions. You can also use GPT-4 for AI-based help.

---

## ✅ Features

- Detects bad practices in Dockerfiles and Kubernetes YAML
- Shows severity: HIGH, MEDIUM, LOW
- Gives easy-to-understand fix suggestions
- Shows risk score (0–10)
- Can auto-fix some problems
- Export results as PDF, CSV, or TXT
- Optional GPT-4 support (with OpenAI key)
- Simple and clean GUI (built with Tkinter)

---

## 📦 Requirements

- Python 3.10+
- OpenAI API key (if using GPT)

Install packages:

```bash
pip install -r requirements.txt
