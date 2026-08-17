# Database Glossary

## Employee

The `emp` table stores employee information.

Important columns:

- `empno`: employee identifier
- `ename`: employee name
- `job`: employee job title
- `mgr`: manager employee number
- `hiredate`: employee hire date
- `sal`: employee salary
- `comm`: employee commission
- `deptno`: department identifier

## Department

The `dept` table stores department information.

Important columns:

- `deptno`: department identifier
- `dname`: department name
- `loc`: department location

## Salary

Salary is stored in `emp.sal`.

Salary represents the employee's base salary.

## Commission

Commission is stored in `emp.comm`.

Commission represents additional compensation associated with an employee.

A NULL commission means that the employee does not currently have a commission value.

## Total Compensation

Total compensation is calculated as:

salary + commission

When commission is NULL, it must be treated as 0.

In SQL, use:

COALESCE(emp.comm, 0)

Therefore, total compensation should be calculated as:

emp.sal + COALESCE(emp.comm, 0)