
import json
import discord
from discord.ext import commands
from model.db import DatabaseClient
from model.discord_webhook import DiscordWebhook

# dicordのコンフィグファイルを読み込む
with open('config/discord.json', 'r') as f:
    discord_config = json.load(f)

# 削除しない固定ロールを読み込む
static_role_ids = discord_config.get('static_role_ids')

# discord_webhook: INSTANCE GENERATION
discord_webhook = DiscordWebhook(discord_config.get('webhook_url'))

# db: INSTANCE GENERATION
db_client = DatabaseClient()

# db: tbl_groupからgroup_idを指定してdiscord_guild_idを取得
discord_guild_id = db_client.get_discord_guild_id(1)

# db: group_idを指定して所属する全てのユーザの"discord_user_id"とdiscord_rolesを取得
# ユーザー情報を取得
users = db_client.get_users_by_group(1)

# 辞書を作成してユーザー情報を格納
user_roles_dict = {}
for user in users:
    user_roles_dict[user.discord_user_id] = user.discord_roles

# 結果を表示（デバッグ用）
for discord_user_id, discord_roles in user_roles_dict.items():
    print(f"User ID: {discord_user_id}, Roles: {discord_roles}")

# Botのインスタンスを作成
intents = discord.Intents.default()
intents.members = True  # メンバー関連のイベントを受け取るために必要
intents.message_content = True  # メッセージコンテンツのIntentを有効にする

bot = commands.Bot(command_prefix='!', intents=intents)

# Botが起動したときのイベントハンドラ
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await assign_roles_to_all_users()
    await bot.close()  # ロール付与の処理が完了した後にBotを終了

# 全ユーザーにロールを付与する関数
async def assign_roles_to_all_users():
    for discord_user_id, discord_roles in user_roles_dict.items():
        await remove_all_roles(discord_guild_id, discord_user_id)
        await assign_roles_on_startup(discord_guild_id, discord_user_id, discord_roles)
        
# ユーザーのすべてのロールを外す関数
async def remove_all_roles(guild_id, user_id):
    guild = bot.get_guild(guild_id)
    if guild is None:
        print(f"サーバーID {guild_id} が見つかりません。")
        return

    member = guild.get_member(user_id)
    if member is None:
        print(f"ユーザーID {user_id} が見つかりません。")
        return

    # ユーザーのすべてのロールを外す
    current_roles = member.roles
    for role in current_roles:
        if role.name != "@everyone" and role.id not in static_role_ids:  # @everyoneロールと特定のロールは外さない
            try:
                await member.remove_roles(role)
                print(f'{member.name} から {role.name} ロールを外しました。')
            except Exception as e:
                print(f'{role.name} ロールの削除に失敗しました: {e}')

# ユーザーにロールを付与する関数
async def assign_roles_on_startup(guild_id, user_id, role_ids):
    guild = bot.get_guild(guild_id)
    if guild is None:
        print(f"サーバーID {guild_id} が見つかりません。")
        return

    member = guild.get_member(user_id)
    if member is None:
        print(f"ユーザーID {user_id} が見つかりません。")
        return

    # role_idsに記載のロールを付与
    role_ids = json.loads(role_ids) # JSON形式の文字列をリストに変換
    for role_id in role_ids:
        role = guild.get_role(int(role_id)) # DBから取得したrole_idはstr型なのでint型に変換
        if role is None:
            print(f"ロールID {role_id} が見つかりません。")
            continue

        try:
            await member.add_roles(role)
            print(f'{member.name} に {role.name} ロールを付与しました。')
            
        except Exception as e:
            print(f'ロールの付与に失敗しました: {e}')

# Botのトークンを使って実行
token = discord_config.get('token')
print(token)
bot.run(token)

# メッセージを送信
# discord_webhook.send_message("UAPロールが付与されました。")