# mcp_client.py
import asyncio
from fastmcp import Client

MCP_URL = "http://127.0.0.1:8001/mcp"


async def check_record(client, record_id):
    result = await client.call_tool(
        "get_loan_application_status",
        {"record_id": record_id}
    )

    print(f"\nRecord ID: {record_id}")
    print("Response :", result)


async def main():
    async with Client(MCP_URL) as client:
        await check_record(client, "REC0001")
        await check_record(client, "REC0002")


if __name__ == "__main__":
    asyncio.run(main())
