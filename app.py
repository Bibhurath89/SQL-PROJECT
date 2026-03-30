import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from langchain_community.utilities import SQLDatabase
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ---------------------------------------------------
# Streamlit Page Config
# ---------------------------------------------------
st.set_page_config(page_title="AI Text-to-SQL", layout="wide")
st.title("AI Text-to-SQL (Company Database)")

# ---------------------------------------------------
# Database Connection
# ---------------------------------------------------
DATABASE_URI = "sqlite:///company.db"

db = SQLDatabase.from_uri(DATABASE_URI)
engine = create_engine(DATABASE_URI)

# ---------------------------------------------------
# Load Local LLM (Ollama)
# ---------------------------------------------------
llm = ChatOllama(
    model="llama3",
    temperature=0
)

# ---------------------------------------------------
# Prompt Template
# ---------------------------------------------------
prompt = ChatPromptTemplate.from_template("""
You are a senior SQL expert.

Rules:
- Generate ONLY valid SQLite SQL.
- Use proper JOINs where needed.
- Use table aliases when appropriate.
- Do NOT generate DROP, DELETE, UPDATE, INSERT, ALTER statements.
- Return ONLY the SQL query. No explanation.

Database Schema:
{schema}

User Question:
{question}
""")

chain = prompt | llm | StrOutputParser()

schema = db.get_table_info()

# ---------------------------------------------------
# User Input
# ---------------------------------------------------
question = st.text_input("Ask a question about the company database:")

if question:

    # Generate SQL
    raw_sql = chain.invoke({
        "schema": schema,
        "question": question
    })

    # Clean markdown formatting if model returns ```sql blocks
    sql_query = raw_sql.strip().replace("```sql", "").replace("```", "").strip()

    st.subheader("Generated SQL")
    st.code(sql_query, language="sql")

    # ---------------------------------------------------
    # Safety Check
    # ---------------------------------------------------
    forbidden_keywords = ["drop", "delete", "update", "insert", "alter"]

    if any(keyword in sql_query.lower() for keyword in forbidden_keywords):
        st.error("Unsafe query detected. Only SELECT queries are allowed.")
    else:
        try:
            with engine.connect() as connection:
                result = connection.execute(text(sql_query))
                rows = result.fetchall()
                columns = result.keys()

                df = pd.DataFrame(rows, columns=columns)

            st.subheader("Query Result")

            if df.empty:
                st.warning("Query executed successfully but returned no results.")
            else:
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Error executing query: {e}")
