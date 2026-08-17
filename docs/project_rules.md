# SQL Generation Rules

## General Rule

Generated SQL must use only tables and columns that exist in the provided database schema.

## Read Only

Only SELECT statements are allowed.

Do not generate:

- INSERT
- UPDATE
- DELETE
- DROP
- ALTER
- CREATE
- TRUNCATE

## Business Context

When business documentation provides a definition or calculation rule, use that information when generating SQL.

For example, if the documentation states:

Total compensation = salary + commission

then use:

sal + COALESCE(comm, 0)

rather than only using `sal`.

## Department Queries

When the user asks about a department by name, use the department documentation and database schema to determine the correct department.

## Ambiguous Questions

If the question cannot be answered reliably from the schema and retrieved documentation, do not invent columns, tables, or business rules.