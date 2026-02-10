from telethon import TelegramClient
import asyncio
from config import Config

async def main():
    try:
        # Re-using the same session name to ensure we see the same things as the bot
        client = TelegramClient(Config.TELEGRAM_SESSION_NAME, Config.TELEGRAM_API_ID, Config.TELEGRAM_API_HASH)
        await client.start()
        
        print("\n" + "="*50)
        print("FETCHING YOUR CHATS... (Please wait)")
        print("="*50)
        print(f"{'ID':<20} | {'Name'}")
        print("-" * 50)
        
        async for dialog in client.iter_dialogs():
            # Print ID and Name clearly
            print(f"{str(dialog.id):<20} | {dialog.name}")
            
        print("-" * 50)
        print("\n\n>>> ACTION REQUIRED: Copy the ID of the channel you want to listen to and paste it into Config.TELEGRAM_CHANNEL_ID")
        
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    asyncio.run(main())
