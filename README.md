# RAG Text-to-SQL

A Retrieval-Augmented Generation (RAG) based Text-to-SQL application that allows users to ask questions about a relational database using natural language.

The system combines **database schema knowledge, business rules, terminology, and retrieval** to provide context to an LLM before generating SQL queries.

## 🚀 Project Overview

Traditional Text-to-SQL systems often struggle when a database contains:

* Complex schemas
* Ambiguous column names
* Business-specific terminology
* Hidden relationships between tables
* Organization-specific rules

This project addresses those challenges by using **RAG to retrieve relevant database knowledge before SQL generation**.

Instead of relying only on the database schema, the system can retrieve supporting knowledge from documents such as:

* Database glossary
* Business rules
* Department definitions
* Project-specific rules

The retrieved context is then used to improve SQL generation.

---

## 🏗️ Architecture

```text
User Question
      │
      ▼
Natural Language Query
      │
      ▼
RAG Retrieval Layer
      │
      ├── Database Glossary
      ├── Business Rules
      ├── Department Information
      └── Project Rules
      │
      ▼
Relevant Context
      │
      ▼
LLM / SQL Generation
      │
      ▼
Generated SQL
      │
      ▼
SQLite Database
      │
      ▼
Query Result
```

---

## 📁 Project Structure

```text
SQL-PROJECT/
│
├── app.py
│
├── create_db.py
├── company.db
│
├── rag/
│   ├── __init__.py
│   ├── ingest.py
│   └── retriever.py
│
├── docs/
│   ├── business_rules.md
│   ├── database_glossary.md
│   ├── department.md
│   └── project_rules.md
│
├── requirements.txt
└── .gitignore
```

### Main Components

#### `app.py`

Main application entry point.

It connects the user interaction layer with the Text-to-SQL pipeline.

#### `create_db.py`

Creates and/or initializes the example SQLite database used by the project.

#### `company.db`

Sample SQLite database used for demonstrating natural-language-to-SQL queries.

#### `rag/ingest.py`

Handles ingestion of project knowledge and prepares the documents for retrieval.

#### `rag/retriever.py`

Responsible for retrieving relevant knowledge based on the user's question.

#### `docs/`

Contains domain knowledge used by the RAG pipeline.

| File                   | Purpose                                        |
| ---------------------- | ---------------------------------------------- |
| `business_rules.md`    | Business-specific rules and definitions        |
| `database_glossary.md` | Database terminology and column/table meanings |
| `department.md`        | Department-related information                 |
| `project_rules.md`     | Project-specific interpretation rules          |

---

## 🧠 Why RAG?

A Text-to-SQL model may understand SQL syntax but still generate incorrect queries when the meaning of the database is unclear.

For example, a question such as:

> "What is the total compensation for employees in the engineering department?"

may require knowledge about:

* Which table contains employees
* Which columns represent compensation
* What counts as "total compensation"
* How the engineering department is represented
* Whether bonuses or other components should be included

RAG provides this additional context before SQL generation.

This allows the system to ground SQL generation in the **actual database and domain knowledge**.

---

## 🔍 Example Workflow

A user asks:

```text
What is the total compensation for employees in the Engineering department?
```

The system first retrieves relevant information such as:

```text
Database schema
+
Compensation definition
+
Department definition
+
Business rules
```

The retrieved context is then provided to the SQL-generation stage.

The system can generate a query similar to:

```sql
SELECT SUM(...)
FROM employees
WHERE department = 'Engineering';
```

The exact SQL depends on the database schema and business rules.

---

## 🛠️ Technologies

* **Python**
* **SQLite**
* **RAG (Retrieval-Augmented Generation)**
* **Vector-based document retrieval**
* **LLM-based SQL generation**
* **Markdown knowledge documents**

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/Bibhurath89/SQL-PROJECT.git
cd SQL-PROJECT
```

Create a virtual environment:

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Project

Start the application with:

```bash
python app.py
```

If the database needs to be recreated, run:

```bash
python create_db.py
```

---

## 📚 Knowledge Base

The RAG layer currently uses project-specific Markdown documents.

These documents allow the system to understand information that may not be obvious from the database schema alone.

Current knowledge sources include:

```text
docs/
├── business_rules.md
├── database_glossary.md
├── department.md
└── project_rules.md
```

This approach makes it possible to extend the system's domain knowledge without modifying the core application logic.

---

## 🎯 Current Phase — Phase 1

This repository represents the **Phase 1 implementation** of the RAG Text-to-SQL project.

The current focus is on establishing a reliable pipeline for:

1. Understanding the database schema
2. Retrieving relevant domain knowledge
3. Generating SQL from natural-language questions
4. Executing the generated SQL
5. Returning the database result

The project is being developed incrementally with increasing levels of query complexity.

---

## 🔮 Planned Improvements

Future development will focus on improving SQL reliability and making the system more production-ready.

### SQL Validation

Add validation to verify that generated SQL references valid tables and columns.

### Automatic SQL Repair

If generated SQL fails validation or execution, the system will attempt to automatically repair the query.

### Better Schema Grounding

Improve the SQL-generation prompt so that generated queries remain tightly grounded in the available database schema.

### Query Difficulty Testing

Continue testing the system against:

* Easy questions
* Medium questions
* Complex questions

### Phase 2 — User-Uploaded Databases

Planned Phase 2 functionality includes allowing users to upload their own databases and optionally provide supporting documents.

The system will then generate database-specific knowledge automatically.

### Phase 3 — Production Hardening

Future production improvements may include:

* Better error handling
* Query safety controls
* Observability
* Evaluation datasets
* Performance optimization
* Improved retrieval
* Authentication
* Deployment infrastructure

---

## 🧪 Testing Philosophy

The project is evaluated using natural-language questions of different difficulty levels.

Example categories:

```text
Easy
  ↓
Simple filtering and aggregation

Medium
  ↓
Joins + business terminology + aggregation

Hard
  ↓
Multiple joins + complex business rules + nested logic
```

The goal is not simply to generate syntactically valid SQL.

The goal is to generate **semantically correct SQL grounded in the database and domain knowledge**.

---

## 🔐 Security Considerations

This project is intended as a development and demonstration project.

For production deployment, additional protections should be implemented, including:

* SQL query validation
* Read-only database access
* Protection against destructive SQL operations
* Input/output validation
* Secrets management
* Authentication and authorization
* Resource and query-time limits

API keys and other secrets should **never be committed to the repository**.

Use environment variables or a `.env` file locally.

---

## 🤝 Contributing

Contributions, suggestions, and feedback are welcome.

If you find an issue or have an idea for improving the RAG or Text-to-SQL pipeline, feel free to open an issue or submit a pull request.

---

## 📌 Project Status

**Phase 1 — Active Development**

The project is currently being developed and evaluated as a RAG-based Text-to-SQL system.

More advanced SQL validation, automatic repair, evaluation, and user-uploaded database functionality are planned for subsequent phases.

---

## 👤 Author

**Bibhu Rath**

GitHub:
https://github.com/Bibhurath89

---

## ⭐ If You Find This Project Interesting

Feel free to explore the repository, try the application, and provide feedback.

The long-term goal is to build a robust system that can translate natural-language questions into reliable, schema-grounded SQL using **RAG + LLMs**.

