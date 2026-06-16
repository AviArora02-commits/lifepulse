from backend.mcp_server import server as cbs


def main() -> None:
    print("Seed data is JSON-backed and ready.")
    print(cbs.get_account_details("CUST1001"))
    print(f"Transactions: {len(cbs.get_transaction_history('CUST1001'))}")


if __name__ == "__main__":
    main()
