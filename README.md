# 🔍 ForensicTimeline PRO

### Digital Forensics & Evidence Management Desktop Application

**ForensicTimeline PRO** is a Python-based desktop application designed to support basic digital forensic investigations. It helps investigators organize cases, register digital evidence, verify file integrity using SHA-256 hashing, analyze CSV-based system logs, and generate chronological incident timelines.

The project demonstrates how **Data Structures and Algorithms (DSA)** can be applied to practical cybersecurity and digital forensics tasks.

---

## 🎯 Project Objectives

- Organize digital forensic investigation cases.
- Register and manage digital evidence.
- Verify file integrity using SHA-256 hashes.
- Maintain a basic chain-of-custody record.
- Analyze logs from multiple sources.
- Generate chronological event timelines.
- Identify high-severity events and possible incident patterns.
- Generate investigation reports.

## ✨ Key Features

| Feature | Description |
|---|---|
| Case Management | Create and manage investigation cases. |
| Evidence Management | Register evidence files for investigation. |
| SHA-256 Verification | Calculate and compare file hashes. |
| Chain of Custody | Record evidence handling activities. |
| Log Analysis | Import and analyze CSV log files. |
| Event Timeline | Display events in chronological order. |
| Threat Analytics | View severity and event statistics. |
| Incident Detection | Group events occurring within time windows. |
| Report Center | Export investigation reports in PDF, JSON and CSV formats. |
| Audit Trail | Review recorded application activities. |

## 🧠 DSA Algorithms Used

This project implements six important DSA concepts:

| Algorithm | Purpose in Project |
|---|---|
| Merge Sort | Sorts events by timestamp. |
| Binary Search | Finds an event using an exact timestamp in sorted data. |
| Hash Statistics | Counts events by source, type and severity using dictionaries. |
| Top-N Heap | Selects the most severe events. |
| Min-Heap Merge | Combines multiple sorted log sources into one timeline. |
| Incident Windows | Groups events occurring close together within a defined time interval. |

These algorithms make log organization, searching, statistics and incident analysis easier.

## ⚙️ How It Works

1. **Create a Case:** Start a new forensic investigation.
2. **Register Evidence:** Add files and calculate their SHA-256 hashes.
3. **Verify Integrity:** Compare current file hashes with previously stored hashes.
4. **Import Logs:** Load CSV log files from different sources.
5. **Analyze Events:** Sort, search and calculate event statistics.
6. **Review Timeline:** Examine suspicious or high-severity events.
7. **Generate Reports:** Export investigation results.

## 🖥️ Technology Stack

- **Programming Language:** Python
- **GUI:** CustomTkinter
- **Database:** SQLite
- **Data Visualization:** Matplotlib
- **Report Generation:** ReportLab
- **Data Structures:** Lists, Dictionaries and Heaps
- **Algorithms:** Merge Sort, Binary Search and Heap-based operations
- **Hashing:** SHA-256

## 📂 Project Structure

```text
ForensicTimeline-PRO/
│
├── main_advanced.py
├── advanced_core.py
├── forensic_core.py
├── main.py
├── sample_logs.csv
│
├── Test_Samples/
│
├── README.md
└── requirements.txt
```

*Note: `forensic_pro.db` is generated locally by the application when needed.*

## 🚀 Installation & Usage

**1. Clone the repository**

```bash
git clone https://github.com/sami0x-pk/ForensicTimeline-PRO.git
```

**2. Open the project directory**

```bash
cd ForensicTimeline-PRO
```

**3. Install dependencies**

```bash
pip install customtkinter matplotlib pandas reportlab
```

**4. Run the application**

```bash
python main_advanced.py
```

Python and the required dependencies must be installed to run the source version.

## 📄 Sample Log Format

The application accepts CSV log files with the following columns:

```csv
timestamp,source,event_type,severity,details
2026-11-01 10:00:00,Windows-01,Successful Login,LOW,User login
2026-11-01 10:02:00,Firewall-01,Blocked Connection,HIGH,Suspicious connection blocked
2026-11-01 10:04:00,Windows-02,Failed Login,MEDIUM,Authentication failed
```

## 🎓 Academic Purpose

ForensicTimeline PRO is developed as a **Data Structures and Algorithms (DSA) Final Project**. It demonstrates the practical application of sorting, searching, hashing, heaps and time-window analysis in a cybersecurity-related environment.

**Project Presenter:** Abdul Samad  
**Department:** Cybersecurity
**University:** Aror University of Art, Architecture, Design & Heritage, Sukkur

## ⚠️ Project Scope & Limitations

- This is an educational digital forensics prototype.
- It analyzes imported log files; it is not a live network monitoring tool.
- SHA-256 verification checks whether file content matches a previously recorded hash. It does not independently prove file origin or acquisition time.
- The local database and audit records are not guaranteed to be tamper-proof.
- It is not a certified forensic investigation platform.

## 👨‍💻 Author

**Abdul Samad**

GitHub: [@sami0x-pk](https://github.com/sami0x-pk)

---

⭐ If you find this academic project useful, consider giving the repository a star.

**ForensicTimeline PRO — Organize Evidence. Analyze Events. Build Timelines.**
