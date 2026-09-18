
from pathlib import Path
import json
import logging
import sqlite3
from datetime import datetime

from langchain.tools import tool


DATABASE_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "tickets.db"
)

EMPLOYEE_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "employees.json"
)


logger = logging.getLogger(__name__)


def _employee_exists(employee_id: str) -> bool:
    """Check whether the employee exists in local employee data."""

    with open(EMPLOYEE_FILE, "r", encoding="utf-8") as file:
        employees = json.load(file)

    return any(
        employee["employee_id"] == employee_id
        for employee in employees
    )


def _generate_ticket_id(cursor) -> str:
    """Generate the next ticket ID."""

    cursor.execute(
        """
        SELECT ticket_id
        FROM tickets
        ORDER BY ticket_id DESC
        LIMIT 1
        """
    )

    row = cursor.fetchone()

    if row is None:
        return "INC-1001"

    last_number = int(row[0].split("-")[1])

    return f"INC-{last_number + 1:04d}"


@tool
def create_ticket(
    employee_id: str,
    category: str,
    description: str,
    priority: str = "Medium",
) -> dict:
    """
    Create a new IT support ticket.

    The employee must exist and the employee must not already
    have an open or in-progress ticket for the same category.

    Args:
        employee_id: Employee ID of the requester.
        category: IT issue category such as VPN or Laptop.
        description: Description of the issue.
        priority: Ticket priority. Defaults to Medium.

    Returns:
        Details of the created ticket or a validation message.
    """

    employee_id = employee_id.strip()
    category = category.strip()
    description = description.strip()
    priority = priority.strip()

    # Validate required information.
    if not employee_id:
        return {
            "success": False,
            "message": "Employee ID is required.",
        }

    if not category:
        return {
            "success": False,
            "message": "Issue category is required.",
        }

    if not description:
        return {
            "success": False,
            "message": "Issue description is required.",
        }

    # Validate employee.
    try:
        employee_exists = _employee_exists(employee_id)
    except (OSError, json.JSONDecodeError) as error:
        logger.exception(
            "Unable to read employee data: %s",
            error,
        )

        return {
            "success": False,
            "message": "Unable to validate the employee at this time.",
        }

    if not employee_exists:
        return {
            "success": False,
            "message": f"Employee {employee_id} could not be verified.",
        }

    connection = sqlite3.connect(DATABASE_FILE)

    try:
        cursor = connection.cursor()

        # Check for an existing active ticket in the same category.
        cursor.execute(
            """
            SELECT ticket_id, status
            FROM tickets
            WHERE employee_id = ?
              AND LOWER(category) = LOWER(?)
              AND status IN ('Open', 'In Progress')
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (employee_id, category),
        )

        existing_ticket = cursor.fetchone()

        if existing_ticket:
            return {
                "success": False,
                "message": (
                    f"An active {category} ticket already exists: "
                    f"{existing_ticket[0]} ({existing_ticket[1]})."
                ),
                "existing_ticket_id": existing_ticket[0],
                "existing_status": existing_ticket[1],
            }

        ticket_id = _generate_ticket_id(cursor)

        created_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute(
            """
            INSERT INTO tickets (
                ticket_id,
                employee_id,
                category,
                description,
                priority,
                status,
                assigned_team,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_id,
                employee_id,
                category,
                description,
                priority,
                "Open",
                "IT Support",
                created_at,
            ),
        )

        connection.commit()

        return {
            "success": True,
            "ticket_id": ticket_id,
            "employee_id": employee_id,
            "category": category,
            "description": description,
            "priority": priority,
            "status": "Open",
            "assigned_team": "IT Support",
            "created_at": created_at,
        }

    except sqlite3.Error:
        connection.rollback()

        logger.exception(
            "Database error while creating ticket."
        )

        return {
            "success": False,
            "message": (
                "Unable to create the ticket due to a "
                "database error."
            ),
        }

    finally:
        connection.close()
