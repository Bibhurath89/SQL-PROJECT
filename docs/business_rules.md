# Business Rules

## Employee Compensation

Employee salary is stored in the `emp.sal` column.

Employee commission is stored in the `emp.comm` column.

Total compensation is calculated as:

salary + commission

If commission is NULL, it should be treated as zero.

Therefore SQL calculations should use:

sal + COALESCE(comm, 0)

## Employee Department

Each employee belongs to a department through `emp.deptno`.

The employee's `deptno` should be joined with `dept.deptno` when department information is required.

## Employee Identification

`emp.empno` uniquely identifies an employee.

`emp.ename` contains the employee's name.