import re
import sqlite3
from pathlib import Path

import streamlit as st

from langchain_community.utilities import SQLDatabase
from langchain_ollama import OllamaLLM

from rag.retriever import (
    retrieve_context,
    format_retrieved_context,
)


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "company.db"

# Use the model you already have installed.
MODEL_NAME = "gemma3:4b"


# =========================================================
# STREAMLIT CONFIG
# =========================================================

st.set_page_config(
    page_title="RAG Text-to-SQL",
    page_icon="🔎",
    layout="wide",
)


# =========================================================
# DATABASE
# =========================================================

@st.cache_resource
def get_database():
    return SQLDatabase.from_uri(
        f"sqlite:///{DB_PATH}"
    )


db = get_database()


@st.cache_data
def get_schema():
    return db.get_table_info()


@st.cache_data
def get_valid_tables():
    """
    Get the actual table names directly from the database.
    This prevents us from hardcoding emp/dept.
    """

    return db.get_usable_table_names()


# =========================================================
# LLM
# =========================================================

@st.cache_resource
def get_llm():
    return OllamaLLM(
        model=MODEL_NAME
    )


llm = get_llm()


# =========================================================
# SQL CLEANING
# =========================================================

def clean_sql(sql: str) -> str:
    """
    Clean LLM output and extract the actual SQL statement.

    Handles:
    - ```sql ... ```
    - ``` ... ```
    - accidental text before SELECT/WITH
    - accidental text after the SQL
    """

    sql = sql.strip()

    # Remove markdown code fences.
    sql = re.sub(
        r"```sql",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    sql = sql.replace("```", "")

    sql = sql.strip()

    # Find the beginning of the actual SQL.
    # This handles cases such as:
    #
    # ite
    # SELECT ...
    #
    # or:
    # Here is your query:
    # SELECT ...
    match = re.search(
        r"\b(SELECT|WITH)\b",
        sql,
        flags=re.IGNORECASE,
    )

    if match:
        sql = sql[match.start():]

    # Remove common trailing explanation.
    sql = re.split(
        r"\n\s*(Explanation|Note|Reasoning):",
        sql,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    return sql.strip()
    """
    Remove markdown formatting and unnecessary whitespace
    from LLM-generated SQL.
    """

    sql = sql.strip()

    # Remove ```sql
    sql = re.sub(
        r"^```sql\s*",
        "",
        sql,
        flags=re.IGNORECASE,
    )

    # Remove ```
    sql = re.sub(
        r"^```\s*",
        "",
        sql,
    )

    sql = re.sub(
        r"\s*```$",
        "",
        sql,
    )

    return sql.strip()


# =========================================================
# SQL SAFETY
# =========================================================

def is_safe_sql(sql: str) -> bool:
    """
    Allow SELECT statements only.
    """

    sql = clean_sql(sql).strip()

    if not sql:
        return False

    # Must begin with SELECT or WITH.
    if not re.match(
        r"^(select|with)\b",
        sql,
        flags=re.IGNORECASE,
    ):
        return False

    forbidden_patterns = [
        r"\binsert\b",
        r"\bupdate\b",
        r"\bdelete\b",
        r"\bdrop\b",
        r"\balter\b",
        r"\bcreate\b",
        r"\btruncate\b",
        r"\breplace\b",
        r"\battach\b",
        r"\bdetach\b",
    ]

    for pattern in forbidden_patterns:

        if re.search(
            pattern,
            sql,
            flags=re.IGNORECASE,
        ):
            return False

    return True


# =========================================================
# TABLE VALIDATION
# =========================================================

def validate_tables(
    sql: str,
    valid_tables,
):
    """
    Check whether every table referenced by FROM/JOIN
    actually exists in the database.

    Returns:
        list of invalid table names
    """

    sql_lower = sql.lower()

    valid_tables_lower = {
        table.lower()
        for table in valid_tables
    }

    # Find tables after FROM and JOIN.
    table_references = re.findall(
        r"\b(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        sql_lower,
    )

    invalid_tables = [
        table
        for table in table_references
        if table not in valid_tables_lower
    ]

    return invalid_tables


# =========================================================
# GENERATE SQL
# =========================================================

def generate_sql(
    question: str,
    schema: str,
    business_context: str,
):
    """
    Generate SQL using:
    - database schema
    - retrieved business context
    - user question
    """

    prompt = f"""
You are an expert SQLite Text-to-SQL system.

Convert the user's natural-language question into ONE valid
SQLite SELECT query.

IMPORTANT RULES:

1. ONLY use tables that appear EXACTLY in the DATABASE SCHEMA.
2. ONLY use columns that appear EXACTLY in the DATABASE SCHEMA.
3. NEVER invent a table name.
4. NEVER invent a column name.
5. NEVER rename a table.
6. NEVER rename a column.
7. The DATABASE SCHEMA is the final authority for table and
   column names.
8. The RETRIEVED BUSINESS DOCUMENTATION is used to understand
   business meanings and business rules.
9. Follow relevant business rules from the retrieved documentation.
10. Generate only a SELECT query.
11. Do not generate INSERT, UPDATE, DELETE, DROP, ALTER,
    CREATE, TRUNCATE, or other write operations.
12. Return ONLY the SQL query.
13. Do not use markdown code fences.
14. Do not explain the query.
15. Use valid SQLite syntax.

VERY IMPORTANT:

If the business documentation uses natural-language names such
as "employee" or "department", do NOT automatically use those
names as SQL table names.

The actual table names MUST come from the DATABASE SCHEMA.

Before returning the SQL, internally check:

- Does every table exist?
- Does every column exist?
- Are all aliases valid?
- Are joins valid?
- Are the business rules being followed?
- Is the query valid SQLite?

DATABASE SCHEMA:
{schema}

RETRIEVED BUSINESS DOCUMENTATION:
{business_context}

USER QUESTION:
{question}

Return ONLY the final SQL query.
"""

    response = llm.invoke(prompt)

    return clean_sql(response)


# =========================================================
# SQL REPAIR
# =========================================================

def repair_sql(
    question: str,
    schema: str,
    business_context: str,
    bad_sql: str,
    error: str,
):
    """
    Ask the LLM to repair an invalid SQL query.

    This is deliberately limited to one repair attempt.
    """

    prompt = f"""
You are an expert SQLite SQL repair system.

The previous SQL query was invalid.

Your job is to return ONE corrected SQLite SELECT query.

USER QUESTION:
{question}

DATABASE SCHEMA:
{schema}

RETRIEVED BUSINESS DOCUMENTATION:
{business_context}

INVALID SQL:
{bad_sql}

ERROR:
{error}

REPAIR RULES:

1. Use ONLY tables that actually exist in the DATABASE SCHEMA.
2. Use ONLY columns that actually exist in the DATABASE SCHEMA.
3. Never invent a table.
4. Never invent a column.
5. Never use natural-language table names if the schema uses
   different names.
6. Follow the retrieved business rules.
7. Return only a SELECT query.
8. Do not generate INSERT, UPDATE, DELETE, DROP, ALTER,
   CREATE, or TRUNCATE.
9. Use valid SQLite syntax.
10. Do not explain anything.
11. Do not use markdown code fences.

The database schema is the final authority.

Return ONLY the corrected SQL query.
"""

    response = llm.invoke(prompt)

    return clean_sql(response)


# =========================================================
# EXECUTE SQL
# =========================================================

def execute_sql(sql: str):

    connection = sqlite3.connect(DB_PATH)

    try:

        cursor = connection.cursor()

        cursor.execute(sql)

        rows = cursor.fetchall()

        if cursor.description is not None:

            columns = [
                description[0]
                for description in cursor.description
            ]

        else:

            columns = []

        return columns, rows

    finally:

        connection.close()


# =========================================================
# UI
# =========================================================

st.title("🔎 RAG-Powered Text-to-SQL")

st.write(
    """
Ask a natural-language question about the database.

The system retrieves relevant business documentation,
combines it with the real database schema, generates SQL,
validates it, and automatically repairs the query if needed.
"""
)


question = st.text_input(
    "Ask a question",
    placeholder=(
        "What is the total compensation of each employee "
        "in the Sales department?"
    ),
)


if st.button(
    "Generate SQL",
    type="primary",
):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

        st.stop()


    # =====================================================
    # STEP 1 — RETRIEVE BUSINESS CONTEXT
    # =====================================================

    with st.spinner(
        "🔎 Retrieving relevant business context..."
    ):

        try:

            retrieved_documents = retrieve_context(
                question,
                k=2,
            )

            business_context = format_retrieved_context(
                retrieved_documents
            )

        except Exception as e:

            st.error(
                "RAG retrieval failed."
            )

            st.info(
                "Make sure you have run:\n\n"
                "`python rag/ingest.py`"
            )

            st.exception(e)

            st.stop()


    # =====================================================
    # DISPLAY RETRIEVED CONTEXT
    # =====================================================

    with st.expander(
        "📚 Retrieved Business Context",
        expanded=True,
    ):

        if retrieved_documents:

            for i, document in enumerate(
                retrieved_documents,
                start=1,
            ):

                source = document.metadata.get(
                    "source",
                    "unknown",
                )

                st.markdown(
                    f"### Document {i}"
                )

                st.caption(
                    f"Source: {source}"
                )

                st.write(
                    document.page_content
                )

                if i < len(retrieved_documents):

                    st.divider()

        else:

            st.info(
                "No relevant business documentation was found."
            )


    # =====================================================
    # STEP 2 — GET REAL DATABASE SCHEMA
    # =====================================================

    schema = get_schema()

    valid_tables = get_valid_tables()


    with st.expander(
        "🗄️ Database Schema"
    ):

        st.code(
            schema,
            language="sql",
        )

        st.caption(
            "Actual database tables: "
            + ", ".join(valid_tables)
        )


    # =====================================================
    # STEP 3 — GENERATE SQL
    # =====================================================

    with st.spinner(
        "🧠 Generating SQL..."
    ):

        sql = generate_sql(
            question=question,
            schema=schema,
            business_context=business_context,
        )


    # =====================================================
    # STEP 4 — SAFETY CHECK
    # =====================================================

    if not is_safe_sql(sql):

        st.error(
            "The generated SQL was rejected because "
            "it is not a safe SELECT query."
        )

        st.code(
            sql,
            language="sql",
        )

        st.stop()


    # =====================================================
    # STEP 5 — TABLE VALIDATION
    # =====================================================

    invalid_tables = validate_tables(
        sql,
        valid_tables,
    )


    repaired = False


    if invalid_tables:

        st.warning(
            "⚠️ The model generated table name(s) "
            "that do not exist in the database: "
            + ", ".join(invalid_tables)
        )


        with st.spinner(
            "🔧 Automatically repairing SQL..."
        ):

            sql = repair_sql(
                question=question,
                schema=schema,
                business_context=business_context,
                bad_sql=sql,
                error=(
                    "Invalid table name(s): "
                    + ", ".join(invalid_tables)
                ),
            )

        repaired = True


        # Validate repaired SQL again.
        if not is_safe_sql(sql):

            st.error(
                "The repaired SQL was rejected because "
                "it is not a safe SELECT query."
            )

            st.stop()


        repaired_tables = validate_tables(
            sql,
            valid_tables,
        )


        if repaired_tables:

            st.error(
                "Automatic repair still contains invalid "
                "table name(s): "
                + ", ".join(repaired_tables)
            )

            st.stop()


    # =====================================================
    # STEP 6 — EXECUTE SQL
    # =====================================================

    with st.spinner(
        "⚡ Executing SQL..."
    ):

        try:

            columns, rows = execute_sql(sql)


        except Exception as first_error:

            # ---------------------------------------------
            # FIRST EXECUTION FAILED
            # ---------------------------------------------

            st.warning(
                "⚠️ The first SQL query failed. "
                "Attempting automatic repair..."
            )


            with st.spinner(
                "🔧 Repairing SQL using the database error..."
            ):

                repaired_sql = repair_sql(
                    question=question,
                    schema=schema,
                    business_context=business_context,
                    bad_sql=sql,
                    error=str(first_error),
                )


            repaired = True

            sql = repaired_sql


            # ---------------------------------------------
            # CHECK REPAIRED SQL SAFETY
            # ---------------------------------------------

            if not is_safe_sql(sql):

                st.error(
                    "The repaired SQL was rejected because "
                    "it is not a safe SELECT query."
                )

                st.stop()


            # ---------------------------------------------
            # CHECK REPAIRED TABLES
            # ---------------------------------------------

            repaired_tables = validate_tables(
                sql,
                valid_tables,
            )


            if repaired_tables:

                st.error(
                    "The repaired SQL still contains invalid "
                    "table name(s): "
                    + ", ".join(repaired_tables)
                )

                st.stop()


            # ---------------------------------------------
            # SECOND / FINAL EXECUTION ATTEMPT
            # ---------------------------------------------

            try:

                columns, rows = execute_sql(sql)

            except Exception as second_error:

                st.error(
                    "❌ SQL execution failed even after "
                    "automatic repair."
                )

                st.code(
                    sql,
                    language="sql",
                )

                st.error(
                    f"Database error: {second_error}"
                )

                st.stop()


    # =====================================================
    # STEP 7 — SHOW FINAL SQL
    # =====================================================

    st.subheader(
        "🧠 Final SQL"
    )


    if repaired:

        st.success(
            "🔧 SQL was automatically repaired "
            "before execution."
        )


    st.code(
        sql,
        language="sql",
    )


    # =====================================================
    # STEP 8 — SHOW RESULT
    # =====================================================

    st.subheader(
        "📊 Query Result"
    )


    if rows:

        # Convert the result into a dictionary structure
        # that Streamlit can display nicely.

        result_data = [
            dict(zip(columns, row))
            for row in rows
        ]

        st.dataframe(
            result_data,
            use_container_width=True,
        )

    else:

        st.info(
            "The query executed successfully, "
            "but returned no rows."
        )