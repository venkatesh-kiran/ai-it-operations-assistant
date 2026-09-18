
from pathlib import Path
import sqlite3

from langchain.tools import tool


DATABASE_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "tickets.db"
)


@tool
def lookup_ticket(employee_id: str) -> list[dict]:
    """
    Look up support tickets for an employee.

    Use this tool when the user wants to know the status
    or details of an existing IT support ticket.

    Args:
        employee_id: Employee ID used to search the ticket database.

    Returns:
        A list of tickets belonging to the employee.
    """

    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                ticket_id,
                employee_id,
                category,
                description,
                priority,
                status,
                assigned_team,
                created_at
            FROM tickets
            WHERE employee_id = ?
            ORDER BY created_at DESC
            """,
            (employee_id,)
        )

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()
