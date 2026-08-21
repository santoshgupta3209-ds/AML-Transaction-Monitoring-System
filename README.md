# 🏦 Finova Bank – AML Transaction Monitoring System

## 📌 Overview

**Finova Bank AML Transaction Monitoring System** is a machine-learning-based application designed to detect and monitor potentially suspicious financial transactions.

The system analyzes customer transaction data, identifies unusual transaction patterns, and helps financial institutions flag transactions that may require further investigation.

The project combines **Machine Learning, FastAPI, Python, MySQL, Data Science, and Git/GitHub** to build an end-to-end AML monitoring solution.

## 🎯 Objectives

* Detect potentially suspicious transactions
* Identify unusual transaction patterns
* Calculate transaction risk
* Flag high-risk transactions for investigation
* Provide a backend API for AML monitoring
* Store and manage transaction and customer data
* Support scalable and automated transaction monitoring

## 🛠️ Technologies Used

| Technology      | Purpose                       |
| --------------- | ----------------------------- |
| 🐍 Python       | Backend & Machine Learning    |
| ⚡ FastAPI       | REST API development          |
| 🤖 XGBoost      | Transaction risk prediction   |
| 🧮 Pandas       | Data processing               |
| 🔢 NumPy        | Numerical computation         |
| 📊 Scikit-learn | ML preprocessing & evaluation |
| 🗄️ MySQL       | Database management           |
| 🔐 Pydantic     | Data validation               |
| 🐙 Git          | Version control               |
| 🌐 GitHub       | Source code management        |
| 🚀 Uvicorn      | FastAPI server                |

## 🧠 Machine Learning

The system uses machine learning to identify suspicious transaction behavior.

### Model Pipeline

```text
Transaction Data
       ↓
Data Cleaning
       ↓
Feature Engineering
       ↓
Data Preprocessing
       ↓
Machine Learning Model
       ↓
Risk Prediction
       ↓
Suspicious Transaction Flag
```

### Key Transaction Features

* Transaction amount
* Transaction type
* Customer ID
* Account information
* Transaction frequency
* Transaction location
* Transaction time
* Previous transaction behavior
* Risk-related transaction patterns

## 📂 Project Structure

```text
api_project/
├── app/
│   ├── __pycache__/
│   ├── api/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── customer.py
│   │   ├── notifications.py
│   │   └── transactions.py
│   ├── ml/
│   │   └── __pycache__/
│   ├── models/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── account.py
│   │   ├── aml_alert.py
│   │   ├── audit_log.py
│   │   ├── customer.py
│   │   ├── notification.py
│   │   ├── transaction.py
│   │   └── user.py
│   ├── schemas/
│   ├── services/
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── aml_service.py
│   │   ├── auth_service.py
│   │   ├── notification_service.py
│   │   └── transaction_service.py
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   └── security.py
├── dataset/
├── frontend/
│   ├── admin-dashboard.html
│   ├── admin-transactions.html
│   ├── alerts.html
│   ├── customer-dashboard.html
│   ├── customers.html
│   ├── index.html
│   ├── login.html
│   ├── logo.png
│   ├── notifications.html
│   ├── styles.css
│   ├── transaction-history.html
│   ── transactions.html
├── tests/
── venv/
├── .env
├── .gitignore
├── aml_db.sqlite3
├── README.md
└── requirements.txt
```

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/finova-aml-monitoring.git
```

```bash
cd finova-aml-monitoring
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 🗄️ Database Configuration

Configure your MySQL database in the application's database configuration.

Example:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=finova_aml
DB_USER=root
DB_PASSWORD=your_password
```

> Do not commit real database passwords or API keys to GitHub.

## 🚀 Run the Application

Start the FastAPI server using:

```bash
uvicorn app.main:app --reload
```

The application will run locally at:

```text
http://127.0.0.1:8000
```

### 📚 API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## 🔍 AML Monitoring Workflow

```text
Customer
   ↓
Transaction
   ↓
Transaction Validation
   ↓
Feature Extraction
   ↓
ML Risk Prediction
   ↓
Risk Score
   ↓
┌──────────────────────┐
│   Transaction Risk   │
├──────────────────────┤
│ Low                  │
│ Medium               │
│ High                 │
└──────────────────────┘
   ↓
High-Risk Alert
   ↓
Investigation
```


## 🔐 Security

The system is designed with security and data protection in mind.

* Input validation using Pydantic
* Authentication and authorization
* Secure database configuration
* Environment variables for sensitive credentials
* Password protection
* API validation
* `.gitignore` for sensitive files

## 📊 Future Enhancements

* Real-time transaction monitoring
* Advanced fraud detection
* Customer risk profiling
* Automated AML alerts
* Email/SMS alert notifications
* Admin dashboard
* Transaction visualization
* Explainable AI for AML predictions
* Docker deployment
* Cloud deployment using AWS
* CI/CD pipeline using GitHub Actions

## 👨‍💻 Author

**Santosh Gupta**

BSc Data Science
Aspiring Backend / Software Developer
Mumbai, India

## ⭐ Project

If you find this project useful, consider giving the repository a ⭐ on GitHub.

---

### ⚠️ Disclaimer

This project is developed for **educational and demonstration purposes**. It is not intended to replace professional AML compliance systems, regulatory processes, or financial institution risk-management procedures.
