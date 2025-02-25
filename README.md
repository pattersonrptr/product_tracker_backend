# Price Monitoring Platform

[![CI/CD](https://github.com/seu-usuario/price-track/actions/workflows/main.yml/badge.svg)](https://github.com/seu-usuario/price-track/actions)  
Monitor products across multiple marketplaces (OLX, Enjoei) and receive alerts when prices drop!

## 🎯 Objective
Automate product price tracking on e-commerce platforms, helping users to:
- Identify **the best times to buy**.
- Avoid **overspending** due to lack of information.
- Centralize data from **different marketplaces**.

## ✨ Features
- 🕷️ **Multi-platform Web Scraper**: OLX, Enjoei (and more, as needed).
- 📉 **Price History**: Interactive graphs (Plotly) for temporal analysis.
- 🔔 **Email Notifications**: Alerts when the price reaches a defined value.
- 🔒 **Security**: JWT authentication and API rate limiting.
- 🧪 **Automated Tests**: 90%+ coverage with pytest.

## 🛠️ Technologies
- **Backend**: Python (FastAPI), Celery, PostgreSQL, Redis.
- **Frontend**: React.js (interactive dashboard).
- **Infrastructure**: Docker, GitHub Actions (CI/CD), AWS/GCP (optional).

## 🚀 Getting Started
### Prerequisites
- Docker and Docker Compose installed.

### Installation
```bash
git clone https://github.com/seu-usuario/price-track.git
cd price-track
docker-compose up --build
