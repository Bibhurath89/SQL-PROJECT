import sqlite3

conn = sqlite3.connect("company.db")
cursor = conn.cursor()

# Enable foreign keys
cursor.execute("PRAGMA foreign_keys = ON;")

# -----------------------
# CREATE TABLES
# -----------------------

cursor.executescript("""

CREATE TABLE IF NOT EXISTS dept (
    deptno INTEGER PRIMARY KEY,
    dname TEXT,
    loc TEXT
);

CREATE TABLE IF NOT EXISTS emp (
    empno INTEGER PRIMARY KEY,
    ename TEXT,
    job TEXT,
    mgr INTEGER,
    hiredate TEXT,
    sal REAL,
    comm REAL,
    deptno INTEGER,
    FOREIGN KEY (deptno) REFERENCES dept(deptno)
);

CREATE TABLE IF NOT EXISTS project (
    proj_id INTEGER PRIMARY KEY,
    proj_name TEXT,
    start_date TEXT,
    end_date TEXT,
    deptno INTEGER,
    FOREIGN KEY (deptno) REFERENCES dept(deptno)
);

CREATE TABLE IF NOT EXISTS emp_project (
    empno INTEGER,
    proj_id INTEGER,
    hours_worked INTEGER,
    PRIMARY KEY (empno, proj_id),
    FOREIGN KEY (empno) REFERENCES emp(empno),
    FOREIGN KEY (proj_id) REFERENCES project(proj_id)
);

CREATE TABLE IF NOT EXISTS salgrade (
    grade INTEGER PRIMARY KEY,
    losal REAL,
    hisal REAL
);

""")

# -----------------------
# INSERT DATA
# -----------------------

cursor.executescript("""

INSERT OR IGNORE INTO dept VALUES (10, 'ACCOUNTING', 'NEW YORK');
INSERT OR IGNORE INTO dept VALUES (20, 'RESEARCH', 'DALLAS');
INSERT OR IGNORE INTO dept VALUES (30, 'SALES', 'CHICAGO');
INSERT OR IGNORE INTO dept VALUES (40, 'OPERATIONS', 'BOSTON');
INSERT OR IGNORE INTO dept VALUES (50, 'IT', 'SAN FRANCISCO');
INSERT OR IGNORE INTO dept VALUES (60, 'HR', 'ATLANTA');

INSERT OR IGNORE INTO salgrade VALUES (1, 0, 19999);
INSERT OR IGNORE INTO salgrade VALUES (2, 20000, 29999);
INSERT OR IGNORE INTO salgrade VALUES (3, 30000, 39999);
INSERT OR IGNORE INTO salgrade VALUES (4, 40000, 49999);
INSERT OR IGNORE INTO salgrade VALUES (5, 50000, 100000);

INSERT OR IGNORE INTO project VALUES (101, 'ERP Implementation', '2023-01-01', '2023-12-31', 10);
INSERT OR IGNORE INTO project VALUES (102, 'AI Chatbot', '2023-03-01', NULL, 50);
INSERT OR IGNORE INTO project VALUES (103, 'Website Redesign', '2023-05-01', NULL, 30);
INSERT OR IGNORE INTO project VALUES (104, 'Payroll Revamp', '2023-04-15', '2023-10-30', 60);
INSERT OR IGNORE INTO project VALUES (105, 'CRM Migration', '2023-06-01', NULL, 20);

INSERT OR IGNORE INTO emp VALUES (1001, 'SMITH', 'CLERK', 1003, '2021-01-10', 20000, NULL, 20);
INSERT OR IGNORE INTO emp VALUES (1002, 'ALLEN', 'SALESMAN', 1003, '2021-03-12', 30000, 1500, 30);
INSERT OR IGNORE INTO emp VALUES (1003, 'WARD', 'MANAGER', 1006, '2019-06-15', 45000, NULL, 30);
INSERT OR IGNORE INTO emp VALUES (1004, 'JONES', 'HR EXEC', 1009, '2020-11-05', 40000, NULL, 60);
INSERT OR IGNORE INTO emp VALUES (1005, 'MARTIN', 'CLERK', 1004, '2022-02-10', 18000, NULL, 60);
INSERT OR IGNORE INTO emp VALUES (1006, 'BLAKE', 'DIRECTOR', NULL, '2018-07-23', 75000, NULL, 30);
INSERT OR IGNORE INTO emp VALUES (1007, 'KING', 'CEO', NULL, '2015-01-01', 90000, NULL, 10);
INSERT OR IGNORE INTO emp VALUES (1008, 'ADAMS', 'DEVELOPER', 1003, '2022-03-15', 35000, NULL, 50);
INSERT OR IGNORE INTO emp VALUES (1009, 'FORD', 'MANAGER', 1006, '2019-08-10', 50000, NULL, 60);

INSERT OR IGNORE INTO emp_project VALUES (1001, 101, 120);
INSERT OR IGNORE INTO emp_project VALUES (1002, 102, 100);
INSERT OR IGNORE INTO emp_project VALUES (1003, 101, 200);
INSERT OR IGNORE INTO emp_project VALUES (1004, 104, 180);
INSERT OR IGNORE INTO emp_project VALUES (1005, 104, 100);
INSERT OR IGNORE INTO emp_project VALUES (1008, 102, 160);
INSERT OR IGNORE INTO emp_project VALUES (1009, 105, 140);

""")

conn.commit()
conn.close()

print("Database created successfully!")