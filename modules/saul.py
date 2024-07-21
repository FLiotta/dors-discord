# DORS related modules
from disnake import ApplicationCommandInteraction, File, User
from dors import slash_command

# Command related modules
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import time
from typing import List, Tuple

WIDTH = 270
HEIGHT = 300
FRAMES = 229
FONT_COLOR = "#FFF"
FONT = ImageFont.truetype("arial.ttf", 20)


def break_text_to_canvas(text: str) -> Tuple[str, float]:
    parsed_string = ""
    substring_length = 0
    text_length = 0

    for word in text.split(" "):
        word_length = FONT.getlength(word)

        if text_length == 0:
            text_length = word_length

        if substring_length + word_length > WIDTH:
            parsed_string += "\n"

            if substring_length > text_length:
                text_length = substring_length

            substring_length = 0
        else:
            substring_length += word_length

        parsed_string += word + ' '

    return parsed_string, text_length


async def create_gif(quotes: List[str]) -> BytesIO:
    time_start = time.time()
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
                    xy=((WIDTH - text_width) / 2, HEIGHT - h - 50), 
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
    
    time_end = time.time()

    print(f"[*] Gif Completed in {int(time_end - time_start)}s")

    return gif_io

@slash_command(name="saul", description="Better call saul!")
async def foo(interaction: ApplicationCommandInteraction, user: User, msg_qty: int = 3):
    channel = interaction.channel

    # Fetch the last 100 messages in the channel
    messages = await channel.history(limit=100).flatten()
    
    # Filter messages by the specified user
    user_messages = [msg for msg in messages if msg.author == user]
    
    if not user_messages:
        return

    # Get the last messages from the user
    user_messages = user_messages[:msg_qty]
    user_messages.reverse()
    
    async with channel.typing():
        gif = await create_gif([msg.content for msg in user_messages])
    
    await user_messages[0].add_reaction("🧑🏻‍⚖️")
    await user_messages[0].add_reaction("⚖️")
    
    await user_messages[0].reply(file=File(fp=gif, filename='animated.gif'))

