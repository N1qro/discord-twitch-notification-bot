import asyncio
import os
from http import HTTPStatus
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
        async with aiohttp.ClientSession(headers=cls.headers) as session:
            newUrl = cls.streams_endpoint + \
                f"?type=all&first={len(ids)}&" + \
                "&".join([f"user_id={uid}" for uid in ids])

            response = await session.get(url=newUrl)
            data = await response.json()
            return data["data"]

    @classmethod
    async def checkIfOnline(cls, id):
        return await cls.getOnlineInfo(id) != []


async def main():
    import dotenv
    import pprint
    dotenv.load_dotenv()

    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    TwitchRequests.init()
    id1 = 698949731
    id2 = 44390855
    data = await TwitchRequests.getOnlineInfo(id1, id2)

    for index, row in enumerate(data, start=1):
        print(f"ROW: {index}")
        pprint.pprint(row)


if __name__ == "__main__":
    asyncio.run(main())