import asyncio
import math
import os
from http import HTTPStatus
from typing import Union

import aiohttp


class Request:
    # // Мета
    clientID = authorization = headers = None

    # // Endpoints
    user_endpoint = "https://api.twitch.tv/helix/users"
    streams_endpoint = "https://api.twitch.tv/helix/streams"

    @classmethod
    def init(cls):
        cls.clientID = os.getenv("CLIENT_ID")
        cls.authorization = f"Bearer {os.getenv('ACCESS_TOKEN')}"
        cls.headers = {
            "Client-ID": cls.clientID,
            "Authorization": cls.authorization
        }

    @classmethod
    async def getChannelInfo(cls, url: str) -> Union[dict, None]:
        if url.startswith("http") and not \
           url.startswith("https://www.twitch.tv/"):
            return HTTPStatus.BAD_REQUEST

        login = url[url.rfind("/") + 1:]
        async with aiohttp.ClientSession(headers=cls.headers) as session:
            response = await session.get(url=cls.user_endpoint, params={"login": login})
            data = await response.json()
            if data.get("error"):
                return data["status"]

            if data.get("data"):
                return data["data"][0]

    @classmethod
    async def getOnlineInfo(cls, *ids):
        """
            Accepts `N` amount of ids and returns a list of dictionaries if any of them are online
            Returns only dictionaries of channels which are online at the moment.
        """
        ids = list(ids)

        bundles = []
        while len(ids) >= 100:
            bundles.append(ids[:100])
            del ids[:100]
        if ids:
            bundles.append(ids[:])

        async with aiohttp.ClientSession(headers=cls.headers) as session:
            tasks = []
            for bundle in bundles:
                newUrl = cls.streams_endpoint + \
                    f"?type=all&first={len(bundle)}&" + \
                    "&".join([f"user_id={uid}" for uid in bundle])

                tasks.append(session.get(url=newUrl))

            meta = []
            for response in await asyncio.gather(*tasks, return_exceptions=True):
                data = await response.json()
                meta.extend(data["data"])

            return meta

    @classmethod
    async def checkIfOnline(cls, id):
        return await cls.getOnlineInfo(id) != []
