from datetime import datetime
from typing import Optional

from aiohttp import ClientSession

from .errors import handle_errors
from .models import ShortURL


class ZShort:
    """
    ZShort API Wrapper.

    Attributes:
        host: Remote host to connect to, default 'https://zs.zevs.me'
        token: Token to use, default None
    """

    def __init__(self, host: Optional[str] = "https://zs.zevs.me", token: Optional[str] = None):
        self.host = host
        self.token = token
        self.base_url = self.host + "/api/v1"
        self._session = ClientSession()
        if self.token:
            self._session.headers.update({"Authorization": f"Bearer {self.token}"})

    async def login(self, username: str, password: str) -> None:
        """
        Login to ZShort.

        Args:
            username: Username
            password: Password
        """
        response = await self._session.post(
            self.base_url + "/auth/token", json={"username": username, "password": password}
        )
        data = await handle_errors(response)
        self.token = data.get("access_token")
        self._session.headers.update({"Authorization": f"Bearer {self.token}"})

    async def register(self, username: str, password: str, invite: str) -> None:
        """
        Register a new account. Requires an invite token from an existing user.

        Args:
            username: New username to register with
            password: Password
            invite: Invite token
        """
        response = await self._session.post(
            self.base_url + "/auth/register",
            json={"username": username, "password": password, "invite": invite},
        )
        data = await handle_errors(response)
        self.token = data.get("access_token")
        self._session.headers.update({"Authorization": f"Bearer {self.token}"})

    async def get(self, slug: str) -> ShortURL:
        """
        Get a Short URL from a slug

        Args:
            slug: Slug to get
        """
        response = await self._session.get(self.base_url + "/short/" + slug)
        data = await handle_errors(response)
        data["url"] = self.host + f"/{slug}"
        return ShortURL(**data)

    async def create(
        self,
        url: str,
        slug: Optional[str] = None,
        title: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> ShortURL:
        """
        Create a new Short URL.

        Args:
            url: URL to shorten
            slug: Custom slug to use
            title: Title to identify by
            expires_at: Expire the URL at this time

        Returns:
            New Short URL, or existing one if a duplicate slug is sent
        """
        if not self.token:
            raise ValueError("Please login with `Zshort.login()`")
        response = await self._session.post(
            self.base_url + "/short/",
            json={"url": url, "slug": slug, "title": title, "expires_at": expires_at},
        )
        if response.status != 409:
            data = await handle_errors(response)
        else:
            data = await response.json()
            data = data.get("short")

        data["url"] = self.host + f"/{slug}"
        return ShortURL(**data)

    async def edit(
        self,
        slug: str,
        url: Optional[str] = None,
        new_slug: Optional[str] = None,
        title: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> ShortURL:
        """
        Edit a short URL.

        Args:
            url: URL to shorten
            slug: Custom slug to use
            title: Title to identify by
            expires_at: Expire the URL at this time

        Returns:
            Edited Short URL, or existing one if a duplicate slug is sent
        """
        if not self.token:
            raise ValueError("Please login with `ZShort.login()`")
        response = await self._session.patch(
            self.base_url + "/short/" + slug,
            json={"url": url, "slug": new_slug, "title": title, "expires_at": expires_at},
        )
        if response.status != 409:
            data = await handle_errors(response)
        else:
            data = await response.json()
            data = data.get("short")

        data["url"] = self.host + f"/{slug}"
        return ShortURL(**data)

    async def delete(self, slug: str) -> None:
        """
        Delete an existing short URL.

        Args:
            slug: Slug of short URL to delete
        """
        if not self.token:
            raise ValueError("Please login with `ZShort.login()`")
        response = await self._session.delete(self.base_url + "/short/" + slug)
        await handle_errors(response)
