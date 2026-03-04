# Frontend Architecture (Flutter Web)

## Overview

The frontend is built using **Flutter Web** and provides the user interface for interacting with the AI questionnaire system.

Users can:

* sign up
* log in
* upload documents
* generate answers
* review answers
* export documents

---

# Frontend Architecture

```
Flutter UI
   │
   ▼
API Service
   │
   ▼
FastAPI Backend
```

---

# Folder Structure

```
lib/
│
├── services/
│     api_service.dart
│
├── models/
│     answer_model.dart
│
├── screens/
│     login_screen.dart
│     signup_screen.dart
│     dashboard_screen.dart
│     upload_screen.dart
│     review_screen.dart
│
└── widgets/
      primary_button.dart
```

---

# Screen Flow

```
Login
 │
 ▼
Dashboard
 │
 ├── Upload Documents
 ├── Generate Answers
 ├── Review Answers
 └── Export Document
```

---

# API Communication

All HTTP calls are centralized in:

```
api_service.dart
```

Example endpoints:

```
POST /auth/signup
POST /auth/login
POST /upload/reference
POST /upload/questionnaire
POST /rag/generate
GET  /review/{id}
PATCH /review/{id}
POST /export/{id}
```

---

# Authentication Flow

```
Login
  │
  ▼
Receive JWT
  │
  ▼
Store in SharedPreferences
  │
  ▼
Attach token to requests
```

---

# Document Upload Flow

```
User Selects PDF
       │
       ▼
File Picker
       │
       ▼
Multipart Request
       │
       ▼
Backend Upload
```

---

# Local Setup

Install dependencies

```
flutter pub get
```

Run web version

```
flutter run -d chrome
```

---

# Build Production

```
flutter build web
```

---

# Deployment

Frontend is hosted using **Firebase Hosting**.

Deployment steps:

```
flutter build web
firebase deploy
```

---

# Future Improvements

* better UI styling
* document preview
* progress indicators
* better error handling
