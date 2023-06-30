from discord import AutocompleteContext


async def getLinkedStreamers(ctx: AutocompleteContext):
    """Возвращает все имена стримеров, привязанные к серверу"""
    autocomplete = []
    for role in ctx.interaction.guild.roles:
        if role.name.startswith("t.tv/"):
            autocomplete.append(role.name[5:])
    return sorted(autocomplete)


async def getSubbedStreamers(ctx: AutocompleteContext):
    """Возвращает все имена стримеров, на которые подписан пользователь"""
    autocomplete = []
    for role in ctx.interaction.user.roles:
        if role.name.startswith("t.tv/"):
            autocomplete.append(role.name[5:])
    return sorted(autocomplete)


async def getUserSubbedStreamers(member):
    lst = []
    for role in member.roles:
        if role.name.startswith("t.tv/"):
            lst.append(role.name[5:])
    return sorted(lst)


async def getUnsubbedStreamers(ctx: AutocompleteContext):
    """Возвращает все имена стримеров, на которых пользователь не подписан"""
    allRoles = set(r.name[5:] for r in ctx.interaction.guild.roles
                   if r.name.startswith("t.tv/"))
    userRoles = set(r.name[5:] for r in ctx.interaction.user.roles
                    if r.name.startswith("t.tv"))

    return sorted(allRoles.difference(userRoles))
