from aiohttp import ClientResponse


class HTTPError(Exception):
    def __init__(self, response: ClientResponse, message: str, **kwargs) -> None:
        self.response = response
        self.status: int = response.status
        self.reason: str = response.reason
        self.message = message

        super().__init__(f"{self.status}|{self.reason}: {self.message}")


async def handle_errors(response: ClientResponse) -> dict:
    """
    Handle HTTP errors.

    Args:
        response: aiohttp.ClientResponse

    Returns:
        JSON response if no error
    """
    data = None
    if 400 <= response.status < 500:
        data = await response.json()
        message = data.get("error") or "Missing required arguments"
        raise HTTPError(response=response, message=message)
    elif response.status >= 500:
        response.raise_for_status()
    else:
        return await response.json()
