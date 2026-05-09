import discord, logging, threading, asyncio, re
from discord.ext import tasks, commands
from db_handler import DBManager
from youtube_handler import YouTubeManager
from config_handler import BotConfig
from gui_handler import BotDashboard, DashBoardHandler, VERSION
from extractor import YouTubeLinkExtractor

conf = BotConfig(); db = DBManager(conf.db_path); yt = YouTubeManager(conf.base_dir); dashboard = None

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=discord.Intents.all())
    async def setup_hook(self):
        await self.tree.sync()
        self.process_queue_task.start()

    @tasks.loop(hours=1)
    async def process_queue_task(self):
        queue = db.get_queue()
        for v_id, p_id in queue:
            success, is_quota = await yt.add_video_to_playlist(v_id, p_id)
            if success:
                db.save_video(v_id); db.clear_from_queue(v_id, p_id)
            elif is_quota: break

    async def global_sync_task(self):
        logging.info("全チャンネル同期開始...")
        count = 0
        for row in db.get_all_settings():
            cid, pid, enabled, _ = row
            channel = self.get_channel(int(cid))
            if not channel or not enabled: continue
            try:
                async for m in channel.history(limit=100):
                    if m.author.bot: continue
                    v_ids = YouTubeLinkExtractor.extract_video_ids(m.content)
                    for v_id in v_ids:
                        if not db.is_video_processed(v_id):
                            success, _ = await yt.add_video_to_playlist(v_id, pid)
                            if success: db.save_video(v_id); count += 1
            except Exception as e: logging.error(f"Sync error {cid}: {e}")
        logging.info(f"同期完了: {count}件追加")

bot = MyBot()

def check_perm(intx: discord.Interaction):
    if str(intx.user.id) == conf.admin_id: return True
    cfg = db.get_channel_config(intx.channel_id)
    if cfg and cfg["allowed_role_id"]:
        role = intx.guild.get_role(int(cfg["allowed_role_id"]))
        if role in intx.user.roles: return True
    return intx.user.guild_permissions.administrator

@bot.tree.command(name="yt_setup")
async def yt_setup(intx: discord.Interaction, playlist_url: str, role: discord.Role = None):
    if not check_perm(intx): return await intx.response.send_message("❌ 権限なし", ephemeral=True)
    match = re.search(r"list=([A-Za-z0-9_-]+)", playlist_url)
    pid = match.group(1) if match else playlist_url.strip()
    db.set_channel_config(intx.channel_id, playlist_id=pid, role_id=str(role.id) if role else None)
    await intx.response.send_message(f"✅ 設定完了: `{pid}`", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot: return
    cfg = db.get_channel_config(message.channel.id)
    if cfg and cfg["is_enabled"]:
        v_ids = YouTubeLinkExtractor.extract_video_ids(message.content)
        for v_id in v_ids:
            if db.is_video_processed(v_id): continue
            success, is_quota = await yt.add_video_to_playlist(v_id, cfg["playlist_id"])
            if success: db.save_video(v_id)
            elif is_quota: db.add_to_queue(v_id, cfg["playlist_id"])
    await bot.process_commands(message)

def run_bot():
    try: yt.authenticate(); bot.run(conf.discord_token)
    except Exception as e: logging.critical(f"Bot Error: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    if conf.discord_token != "ENTER_TOKEN":
        dashboard = BotDashboard(conf, db, bot)
        logging.getLogger().addHandler(DashBoardHandler(dashboard._append_log))
        threading.Thread(target=run_bot, daemon=True).start()
        dashboard.run()