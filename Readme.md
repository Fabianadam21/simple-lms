# 📚 Simple LMS - Django + Docker

## 📌 Deskripsi

Project ini merupakan implementasi **Simple Learning Management System (LMS)** menggunakan:

* 🐍 Django (Web Framework)
* 🐳 Docker (Containerization)
* 🐘 PostgreSQL (Database)

Project ini dibuat untuk memenuhi tugas setup environment development menggunakan Docker dan Django.

---

## 🧱 Project Structure

```
simple-lms/
├── docker-compose.yml
├── Dockerfile
├── .env
├── .env.example
├── requirements.txt
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── README.md
```

---

## 🚀 Cara Menjalankan Project

### 1. Clone Repository

```
git clone https://github.com/Fabianadam21/simple-lms.git
cd simple-lms
```

---

### 2. Copy File Environment

```
cp .env.example .env
```

---

### 3. Jalankan Docker

```
docker-compose up --build
```

---

### 4. Jalankan Migration

Buka terminal baru:

```
docker-compose exec web python manage.py migrate
```

---

### 5. Akses Aplikasi

Buka browser:

```
http://localhost:8000
```

---

## ⚙️ Environment Variables

| Variable    | Deskripsi         |
| ----------- | ----------------- |
| DEBUG       | Mode debug Django |
| SECRET_KEY  | Secret key Django |
| DB_NAME     | Nama database     |
| DB_USER     | User database     |
| DB_PASSWORD | Password database |
| DB_HOST     | Host database     |
| DB_PORT     | Port database     |

---

## 🗄️ Database

Menggunakan **PostgreSQL** yang berjalan di dalam Docker container.

---

## 📦 Services (Docker)

* **Web** → Django Application
* **Database** → PostgreSQL

---

## 📸 Screenshot

Tambahkan screenshot berikut:

* Halaman utama (`localhost:8000`)
* Terminal Docker berjalan
* Hasil migrate database

---

## 🔥 Fitur

* Setup Django dengan Docker
* Integrasi PostgreSQL
* Environment variable configuration
* Struktur project clean & scalable

---

## 👨‍💻 Author

**Fabian Adam Maheswara**

---

## ✨ Notes

* Pastikan Docker Desktop sudah running
* Gunakan `--noreload` untuk menghindari bug di Windows
* Gunakan terminal baru saat menjalankan migrate

---
