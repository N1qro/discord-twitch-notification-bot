from enum import Enum
from typing import Union
from dataclasses import dataclass


class Status(Enum):
    good = "✅ Done"
    bad = "❌ Not given"


@dataclass
class GuildData:
    guildId: int
    channelId: Union[int, None]
    roleId: Union[int, None]

    def __iter__(self):
        return iter((self.guildId, self.channelId, self.roleId))
