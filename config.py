import os

class config:
    channel_id = 0 # チャンネルのIDを入れる
    token = ""  # Discordのトークンを入れる
    gets_from_environment = True # 環境変数から入力するかどうか
    # DISCORD_BOT_CHANNEL_ID と DISCORD_BOT_TOKEN の環境変数にお願いします
    def __init__(self):
        if config.gets_from_environment:
            config.channel_id = os.environ.get('DISCORD_BOT_CHANNEL_ID')
            config.token = os.environ.get('DISCORD_BOT_TOKEN')

if __name__ == '__main__':
    test = config()