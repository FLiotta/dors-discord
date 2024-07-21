# DORS related modules
from disnake import ApplicationCommandInteraction, File, User
from dors import slash_command

# Command related modules
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import List, Tuple

WIDTH = 300
HEIGHT = 270
FRAMES = 229
FONT_COLOR = "#FFF"
FONT = ImageFont.truetype("arial.ttf", 20)

PADDING_BOTTOM = 25


def break_text_to_canvas(text: str) -> Tuple[str, float]:
    """
    Receives a string and returns it with break-line namespaces when it exceeds the image width.

    It also returns text's width
    """
    parsed_string = ""
    substring_length = 0
    longest_string_length = 0

    for word in text.split(" "):
        word_length = FONT.getlength(word + " ")

        # If the next word makes the line exceed the screen width
        if substring_length + word_length > WIDTH:
            # Break line
            parsed_string += "\n"

            # Check if this line was the biggest one
            if substring_length > longest_string_length:
                longest_string_length = substring_length

            substring_length = 0

        # Append the word to the substring
        parsed_string += word + ' '
        substring_length += word_length

    # In case there was no longest_string in the loop (one line phrase)
    if longest_string_length == 0:
        longest_string_length = FONT.getlength(parsed_string)

    return parsed_string, longest_string_length



async def create_gif(quotes: List[str]) -> BytesIO:
    modified_frames = []

    frames_per_quote = round(FRAMES / len(quotes))

    for quote_index, quote in enumerate(quotes):
        parsed_multiline_text, text_width = break_text_to_canvas(quote)
        
        from_index = round(frames_per_quote * quote_index)
        to_index = from_index + frames_per_quote

        for frame_index in range(from_index, to_index):
            with Image.open(f"./frames/frame_{str(frame_index).zfill(3)}.gif") as im:
                new_frame = im.copy()  # Create a copy to modify
                draw = ImageDraw.Draw(new_frame)
                
                _, _, _, h = draw.textbbox((0, 0), parsed_multiline_text, font=FONT)
                
                draw.multiline_text(
                    xy=((WIDTH - text_width) / 2, HEIGHT - h - PADDING_BOTTOM), 
                    text=parsed_multiline_text, 
                    font=FONT, 
                    fill=FONT_COLOR
                )
                modified_frames.append(new_frame)

    gif_io = BytesIO()

    # Ensure modified_frames contains PIL images
    if modified_frames:
        modified_frames[0].save(
            gif_io,
            format='GIF',
            save_all=True,
            append_images=modified_frames[1:],
            duration=28,
            loop=0
        )

    gif_io.seek(0)

    return gif_io

@slash_command(name="saul", description="Better call saul!")
async def saul(
    interaction: ApplicationCommandInteraction, 
    user: User, 
    msg_qty: int = 3,
    query_after_msg_id: str = ""
):
    if msg_qty > 6:
        await interaction.response.send_message(f"Too many messages, maximum is 6", ephemeral=True)

    channel = interaction.channel
    ref_message = None

    if query_after_msg_id:
        ref_message = await channel.fetch_message(int(query_after_msg_id))
        
    messages = await channel.history(limit=100, after=ref_message).flatten()
    
    # Filter messages by the specified user
    user_messages = [msg for msg in messages if msg.author == user]
    
    if not user_messages:
        return

    # Get the last messages from the user
    user_messages = user_messages[:msg_qty]

    if not query_after_msg_id:
        user_messages.reverse()
    
    async with channel.typing():
        gif = await create_gif([msg.content for msg in user_messages])
    
    await user_messages[0].add_reaction("🧑🏻‍⚖️")
    await user_messages[0].add_reaction("⚖️")
    
    await user_messages[0].reply(file=File(fp=gif, filename='animated.gif'))

