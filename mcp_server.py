from fastmcp import FastMCP
from agent import check_loan_application_status

mcp = FastMCP("Cred Banking Support MCP")


@mcp.tool
def get_loan_application_status(record_id: str) -> dict:
    """
    Return loan application status, loan amount, escalation score,
    and escalation flag for a given record ID.
    """
    return check_loan_application_status(record_id)


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8001,
        path="/mcp"
    )
