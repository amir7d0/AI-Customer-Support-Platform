from __future__ import annotations

import json

from .schemas import TicketMetadata
from .sample_data import SAMPLE_EMAIL
from .service import create_support_service


def main() -> None:
    workflow, tools = create_support_service()
    ticket = TicketMetadata.from_email(SAMPLE_EMAIL)
    result = workflow.process_ticket(ticket)

    print("\n=== Processed Support Ticket ===\n")
    print(f"Response:\n{result.get('response')}\n")
    


if __name__ == "__main__":
    main()
