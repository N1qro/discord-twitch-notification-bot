import asyncio
import os
from typing import Union

import aiohttp


class TwitchRequests:
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
    async def getChannelInfo(cls, url) -> Union[dict, None]:
        login = url[url.rfind("/") + 1:]
        async with aiohttp.ClientSession(headers=cls.headers) as session:
            response = await session.get(url=cls.user_endpoint, params={"login": login})
            data = await response.json()
            if data["data"]:
                return data["data"][0]

    @classmethod
    async def areUsersOnline(cls, *ids):
        """
            Accepts `N` amount of ids and returns a list of dictionaries if any of them are online
            Returns only dictionaries of channels which are online at the moment.
        """
        async with aiohttp.ClientSession(headers=cls.headers) as session:
            newUrl = cls.streams_endpoint + \
                f"?type=all&first={len(ids)}&" + \
                "&".join([f"user_id={uid}" for uid in ids])

            response = await session.get(url=newUrl)
            data = await response.json()
            return data["data"]


if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()

    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    TwitchRequests.clientID = os.getenv("CLIENT_ID")
    TwitchRequests.authorization = f"Bearer {os.getenv('ACCESS_TOKEN')}"
    TwitchRequests.headers = {
        "Client-ID": TwitchRequests.clientID,
        "Authorization": TwitchRequests.authorization
    }

    # print(asyncio.run(TwitchRequests.getChannelInfo("https://www.twitch.tv/riotgames")))
    # print(asyncio.run(TwitchRequests.areUsersOnline("39154778", "36029255")))