import discord
from discord.ext import commands
import asyncio
import datetime
import random
import json
import os
import sys
from colorama import Fore, Style, init

init(autoreset=True)

class Config:
    def __init__(self, path="config.json"):
        if not os.path.exists(path):
            print(f"{Fore.RED}[ERROR] config.json not found! Rename config.json.example to config.json")
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    @property
    def token(self): return self.data.get("token")
    @property
    def channel_id(self): return int(self.data.get("target_channel_id"))
    @property
    def kl_amount(self): return self.data.get("kl_amount", "1000")

class LootBot(commands.Bot):
    def __init__(self, config):
        super().__init__(command_prefix="!", self_bot=True, chunk_guilds_at_startup=False)
        self.cfg = config
        self.MUDAE_ID = 432610292342587392
        self.automation_running = True
        self.response_event = asyncio.Event()
        self.arlp_event = asyncio.Event()
        self.last_detected = None 

    def log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        color = {"INFO": Fore.CYAN, "SUCCESS": Fore.GREEN, "WARN": Fore.YELLOW, "ERR": Fore.RED}.get(level, Fore.WHITE)
        print(f"{Fore.WHITE}[{timestamp}]{Style.RESET_ALL}{color}[{level}] {message}")

    async def on_ready(self):
        self.log(f"Authenticated as: {self.user}", "SUCCESS")
        self.log("MudaLoot Engine Started.", "INFO")
        self.loop.create_task(self.automation_engine())

    async def run_arlp_sequence(self, channel):
        """Handle pin limit errors by releasing duplicates."""
        delay = random.uniform(0.8, 1.2)
        self.log("Pin limit detected! Running $arlp sequence...", "WARN")
        await asyncio.sleep(delay)
        
        self.arlp_event.clear()
        await channel.send("$arlp")
        
        try:
            await asyncio.wait_for(self.arlp_event.wait(), timeout=10.0)
            self.log("Pins released successfully via $arlp.", "SUCCESS")
        except asyncio.TimeoutError:
            self.log("Timeout: $arlp confirmation not received.", "ERR")

    async def automation_engine(self):
        await self.wait_until_ready()
        channel = self.get_channel(self.cfg.channel_id)

        if not channel:
            self.log("Invalid Channel ID. Check config.", "ERR")
            return

        while self.automation_running:
            self.response_event.clear()
            self.last_detected = None
            
            self.log(f"Sending Command: $kl {self.cfg.kl_amount}", "INFO")
            await channel.send(f"$kl {self.cfg.kl_amount}")
            
            try:
                # --- PHASE 1: Initial $kl Response ---
                await asyncio.wait_for(self.response_event.wait(), timeout=5.0)
                
                if self.last_detected == "PIN_ERROR":
                    await self.run_arlp_sequence(channel)
                    continue 

                elif self.last_detected == "CONFIRM":
                    self.log("Confirmation requested. Sending 'y'...", "SUCCESS")
                    self.response_event.clear()
                    self.last_detected = None # Reset state for the next check
                    await channel.send("y")
                    
                    # --- PHASE 2: Post-Confirmation ('y') Response ---
                    try:
                        # Mudae might throw "too many pins" AFTER 'y'
                        await asyncio.wait_for(self.response_event.wait(), timeout=4.0)
                        
                        if self.last_detected == "PIN_ERROR":
                            await self.run_arlp_sequence(channel)
                            continue
                        elif self.last_detected == "SUCCESS":
                            self.log("Loot successful.", "SUCCESS")
                    except asyncio.TimeoutError:
                        self.log("No response after 'y', assuming success.", "INFO")

                elif self.last_detected == "SUCCESS":
                    self.log("Direct loot successful.", "SUCCESS")

            except asyncio.TimeoutError:
                self.log("Mudae did not respond to $kl.", "WARN")

            # --- PHASE 3: Randomized Cooldown ---
            wait_time = random.uniform(
                self.cfg.data["settings"]["min_cooldown"], 
                self.cfg.data["settings"]["max_cooldown"]
            )
            self.log(f"Cycle complete. Waiting {wait_time:.2f}s...", "INFO")
            await asyncio.sleep(wait_time)

    async def on_message(self, message):
        if message.channel.id != self.cfg.channel_id or message.author.id != self.MUDAE_ID:
            return

        content = message.content.lower()

        # Confirmation check
        if "do you want to spend" in content and "y/n" in content:
            self.last_detected = "CONFIRM"
            self.response_event.set()
        
        # Success check
        elif any(x in content for x in ["rolls stacked", "kakera", "obtained"]):
            self.last_detected = "SUCCESS"
            self.response_event.set()
        
        # Pin error check (This handles the scenario you provided)
        elif "too many pins" in content or "release your duplicates" in content:
            self.last_detected = "PIN_ERROR"
            self.response_event.set()
        
        # arlp confirmation check
        elif "mudapins were released" in content:
            self.arlp_event.set()

if __name__ == "__main__":
    config = Config()
    bot = LootBot(config)
    try:
        bot.run(config.token)
    except Exception as e:
        print(f"{Fore.RED}[FATAL ERROR] {e}")
