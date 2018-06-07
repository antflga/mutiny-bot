import discord
from discord import Member, Message
from discord.ext import commands
from discord.ext.commands import Context, Bot


class InvalidMention(commands.CheckFailure):
    pass


class NotInGuild(commands.CheckFailure):
    pass


class MissingPermission(commands.CheckFailure):
    pass


class InvalidCommand(commands.CheckFailure):
    pass


def valid_mentions():
    def predicate(ctx: Context):
        msg: Message = ctx.message
        if len(msg.mentions) > 1:
            raise InvalidMention(f'Required 1 mention, got {len(msg.mentions)}')
        elif len(msg.mentions) is 1:
            user_id = msg.mentions[0].id
            author_id = ctx.author.id
            bot_id = ctx.bot.user.id
            if user_id == author_id:
                raise InvalidMention('Self mentions are invalid')
            elif user_id == bot_id:
                raise InvalidMention('Bot mentions are invalid')
            elif len(msg.mentions) is 0 and msg.content is not f"!{ctx.command}":
                raise InvalidCommand(f"Command `{ctx.message.content}` is invalid")
            else:
                return True
        else:
            return True

    return commands.check(predicate)


class Mutiny:
    """Mutiny."""

    def __init__(self, bot):
        self.bot: Bot = bot

    votes = {}

    def get_votes(self, user_id):
        voters = self.votes.get(user_id)
        if voters is None:
            return []
        else:
            return voters

    def user_vote(self, user_id, author_id):
        voters = self.get_votes(user_id)
        if author_id in voters:
            voters.remove(author_id)
        else:
            voters.append(author_id)
        self.votes.update({user_id: voters})

    @valid_mentions()
    @commands.guild_only()
    @commands.command(pass_context=True, cog_name="Mutiny")
    async def mutiny(self, ctx: Context):
        """
        Vote away the freedom of speech
        Usage: !mutiny <user>
        """
        msg: Message = ctx.message
        if len(msg.mentions) is not 0:
            user = msg.mentions[0]
            author: Member = msg.author
            if "mutiny" in [r.name.lower() for r in author.roles]:
                self.user_vote(user.id, author.id)
                num = len(self.get_votes(user.id))
                em = discord.Embed(description=f'\n{num}/5 votes required to mute {user.name}.', colour=0x9370db)
                em.set_thumbnail(url=user.avatar_url)
                em.set_author(name=author.name, icon_url=author.avatar_url)
                await ctx.channel.send(embed=em)
            else:
                raise MissingPermission("Missing mutiny role, unauthorized to mute")
        else:
            raise InvalidMention(f'Required 1 mention')

    @commands.command(pass_context=True, cog_name="Mutiny")
    @valid_mentions()
    @commands.guild_only()
    async def forgive(self, ctx: Context, user: Member):
        """
        Give the gift of free speech (requires mod)
        Usage: !forgive <user>
        """
        msg: Message = ctx.message
        if len(msg.mentions) is not 0:
            self.votes.update({user.id: []})
            author = ctx.author

            if "mods" in [r.name.lower() for r in author.roles]:
                em = discord.Embed(description=f'User {user.mention} forgiven.', colour=0x9370db)
                em.set_thumbnail(url=user.avatar_url)
                em.set_author(name=author.name, icon_url=author.avatar_url)
                await ctx.channel.send(embed=em)
            else:
                raise MissingPermission("Missing mods role, unauthorized to forgive")
        else:
            raise InvalidMention(f'Required 1 mention')

    @mutiny.error
    @forgive.error
    async def mutiny_error(self, ctx: Context, error):
        """
        Handles errors for the Mutiny cog
        """
        command = ctx.command
        em = discord.Embed(title=f"{command.name}: {error}", colour=0x9370db,
                           description=f"Error in command `{ctx.message.content}`\n{command.help}:")
        await ctx.message.delete()
        await ctx.author.send(embed=em)

    async def on_message(self, message):
        votes = self.get_votes(message.author.id)
        if len(votes) >= 5:
            await message.author.send("You've been muted! Contact the moderators.")
            await message.delete()


def setup(bot):
    bot.add_cog(Mutiny(bot))
