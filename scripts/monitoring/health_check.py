"""Health monitoring script."""
import asyncio
import httpx


async def check_health():
    """Check application health."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/api/v1/health")
            print(f"Health Status: {response.json()}")
        except Exception as e:
            print(f"Health check failed: {e}")


if __name__ == "__main__":
    asyncio.run(check_health())
