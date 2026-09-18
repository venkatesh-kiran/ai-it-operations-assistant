import sqlite3

from tools.ticket_creation import create_ticket
from tools.ticket_lookup import lookup_ticket


def test_tc002_ticket_lookup(test_environment):
    """TC-002: Lookup returns the actual tickets for EMP1024."""
    results = lookup_ticket.invoke({"employee_id": "EMP1024"})

    ticket_ids = {ticket["ticket_id"] for ticket in results}

    assert ticket_ids == {"INC-1001", "INC-1004"}


def test_tc003_successful_ticket_creation(empty_ticket_environment):
    """TC-003: A valid request creates a new Open ticket."""
    result = create_ticket.invoke(
        {
            "employee_id": "EMP1002",
            "category": "VPN",
            "description": "I cannot connect to the corporate VPN.",
        }
    )

    assert result["success"] is True
    assert result["ticket_id"] == "INC-1001"
    assert result["priority"] == "Medium"
    assert result["status"] == "Open"
    assert result["assigned_team"] == "IT Support"

    connection = sqlite3.connect(empty_ticket_environment["db"])
    count = connection.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    connection.close()

    assert count == 1


def test_tc004_missing_required_information(empty_ticket_environment):
    """TC-004: Required fields are validated before ticket creation."""
    result = create_ticket.invoke(
        {
            "employee_id": "",
            "category": "Laptop",
            "description": "",
        }
    )

    assert result["success"] is False
    assert "Employee ID is required" in result["message"]

    connection = sqlite3.connect(empty_ticket_environment["db"])
    count = connection.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    connection.close()

    assert count == 0


def test_tc005_invalid_employee(empty_ticket_environment):
    """TC-005: Unknown employee IDs are rejected."""
    result = create_ticket.invoke(
        {
            "employee_id": "EMP9999",
            "category": "Laptop",
            "description": "The laptop is not starting.",
        }
    )

    assert result["success"] is False
    assert "could not be verified" in result["message"]

    connection = sqlite3.connect(empty_ticket_environment["db"])
    count = connection.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    connection.close()

    assert count == 0


def test_tc006_duplicate_ticket_prevention(test_environment):
    """TC-006: An active ticket for the same employee/category blocks duplicates."""
    result = create_ticket.invoke(
        {
            "employee_id": "EMP1024",
            "category": "VPN",
            "description": "I still cannot connect to the corporate VPN.",
        }
    )

    assert result["success"] is False
    assert result["existing_ticket_id"] == "INC-1001"
    assert result["existing_status"] == "In Progress"

    connection = sqlite3.connect(test_environment["db"])
    count = connection.execute(
        """
        SELECT COUNT(*)
        FROM tickets
        WHERE employee_id = 'EMP1024'
          AND LOWER(category) = 'vpn'
        """
    ).fetchone()[0]
    connection.close()

    assert count == 1
