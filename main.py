from telethon import TelegramClient
from telethon.tl.types import PeerChannel, DocumentAttributeVideo
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import FloodWaitError
import asyncio
import tempfile
import os

# API credentials
api_id = '24211934'  # Ganti dengan API ID Anda
api_hash = '1b42778fd00a9a9010d9ddad0a595ed3'  # Ganti dengan API Hash Anda
session_name = 'session_name'

# Source and target channel details
source_channel_id = 2253293576
target_channel_link = "https://t.me/+Bswj6uKsmA4wYjJk"
start_message = 432
end_message = 1050

async def download_and_send_video(message, target, client):
    """Download video from source channel and send to target channel."""
    try:
        # Create a temporary file for downloading video
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            file_path = temp_file.name
            await message.download_media(file=file_path)

        # Upload the video to the target channel
        await client.send_file(target, file_path, caption=message.text or "", parse_mode='html')

        # Delete the temporary file after uploading
        os.remove(file_path)
        print(f"Message {message.id} successfully sent.")
    except Exception as e:
        print(f"Error sending video message {message.id}: {e}")

async def main():
    async with TelegramClient(session_name, api_id, api_hash) as client:
        try:
            # Get source channel entity
            source_channel = await client.get_entity(PeerChannel(source_channel_id))
            print(f"Connected to source channel: {source_channel.title}")

            # Join the target channel and get its entity
            await client(JoinChannelRequest(target_channel_link))
            target_channel = await client.get_entity(target_channel_link)
            print(f"Connected to target channel: {target_channel.title}")

            # Process messages
            async for message in client.iter_messages(
                source_channel,
                reverse=True,
                offset_id=start_message - 1,
                limit=end_message - start_message + 1
            ):
                print(f"Processing message {message.id}...")

                if message.video:
                    print(f"Message {message.id} is a video.")
                    await download_and_send_video(message, target_channel, client)
                elif message.media:
                    # Log details for non-video media
                    print(f"Message {message.id} has media but is not a video: {message.media}")
                else:
                    # Log messages without media
                    print(f"Message {message.id} skipped (no media).")
                await asyncio.sleep(1)  # Delay to avoid rate limits
        except FloodWaitError as e:
            print(f"Rate limit hit, waiting {e.seconds} seconds...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"Critical error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
