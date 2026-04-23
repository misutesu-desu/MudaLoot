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
            print(f"{Fore.RED}[ERROR] config.json not found!")
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    @property
    def token(self): return self.data.get("token")
    @property
    def channel_id(self): return int(self.data.get("target_channel_id"))
    @property
    def kl_amount(self): return self.data.get("kl_amount", "1000")
    @property
    def scrap_target_id(self): return self.data.get("scrap_target_id")
    @property
    def scrap_amount(self): return self.data.get("scrap_amount", "500000000")

class LootBot(commands.Bot):
    def __init__(self, config):
        super().__init__(command_prefix="!", self_bot=True, chunk_guilds_at_startup=False)
        self.cfg = config
        self.MUDAE_ID = 432610292342587392
        self.automation_running = True
        self.response_event = asyncio.Event()
        self.arlp_event = asyncio.Event()
        self.last_detected = None 
        self.selected_mode = None

    def log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        color = {"INFO": Fore.CYAN, "SUCCESS": Fore.GREEN, "WARN": Fore.YELLOW, "ERR": Fore.RED}.get(level, Fore.WHITE)
        print(f"{Fore.WHITE}[{timestamp}]{Style.RESET_ALL}{color}[{level}] {message}")

    async def on_ready(self):
        self.log(f"Authenticated as: {self.user}", "SUCCESS")
        print(f"\n{Fore.CYAN}--- Select Operation Mode ---")
        print(f"{Fore.YELLOW}[1] Kakera Loot ($kl)")
        print(f"{Fore.YELLOW}[2] Give Scrap ($givescrap)")
        
        choice = input(f"{Fore.WHITE}Choice: ")
        if choice == "1":
            self.selected_mode = "KL"
            self.log("Mode set to Kakera Loot.", "INFO")
        elif choice == "2":
            self.selected_mode = "SCRAP"
            self.log(f"Mode set to GiveScrap (Target: {self.cfg.scrap_target_id}).", "INFO")
        else:
            self.log("Invalid choice. Defaulting to KL.", "WARN")
            self.selected_mode = "KL"

        self.loop.create_task(self.automation_engine())

    async def run_arlp_sequence(self, channel):
        """Handle pin limit errors."""
        delay = random.uniform(1.2, 2.5)
        self.log("Pin limit detected! Running $arlp...", "WARN")
        await asyncio.sleep(delay)
        self.arlp_event.clear()
        await channel.send("$arlp")
        try:
            await asyncio.wait_for(self.arlp_event.wait(), timeout=10.0)
            self.log("Pins released.", "SUCCESS")
        except asyncio.TimeoutError:
            self.log("Timeout waiting for $arlp confirmation.", "ERR")

    async def automation_engine(self):
        await self.wait_until_ready()
        channel = self.get_channel(self.cfg.channel_id)

        if not channel:
            self.log("Invalid Channel ID. Check config.", "ERR")
            return

        while self.automation_running:
            self.response_event.clear()
            self.last_detected = None
            
            # --- PHASE 1: Send Command Based on Mode ---
            if self.selected_mode == "KL":
                self.log(f"Sending Command: $kl {self.cfg.kl_amount}", "INFO")
                await channel.send(f"$kl {self.cfg.kl_amount}")
            else:
                self.log(f"Sending Command: $givescrap {self.cfg.scrap_target_id} {self.cfg.scrap_amount}", "INFO")
                await channel.send(f"$givescrap {self.cfg.scrap_target_id} {self.cfg.scrap_amount}")

            try:
                # --- PHASE 2: Wait for Confirmation Prompt ---
                await asyncio.wait_for(self.response_event.wait(), timeout=6.0)
                
                if self.last_detected == "PIN_ERROR":
                    await self.run_arlp_sequence(channel)
                    continue 

                elif self.last_detected == "CONFIRM":
                    # Human-like delay before typing 'y'
                    human_delay = random.uniform(1.1, 2.8)
                    await asyncio.sleep(human_delay)
                    
                    self.log("Confirmation requested. Sending 'y'...", "SUCCESS")
                    self.response_event.clear()
                    await channel.send("y")
                    
                    # Optional wait for final success message
                    try:
                        await asyncio.wait_for(self.response_event.wait(), timeout=4.0)
                    except asyncio.TimeoutError:
                        pass

                elif self.last_detected == "SUCCESS":
                    self.log("Action completed successfully.", "SUCCESS")

            except asyncio.TimeoutError:
                self.log("Mudae did not respond. Retrying next cycle.", "WARN")

            # --- PHASE 3: Randomized Cooldown Between Cycles ---
            wait_time = random.uniform(
                self.cfg.data["settings"]["min_cooldown"], 
                self.cfg.data["settings"]["max_cooldown"]
            )
            self.log(f"Cycle finished. Waiting {wait_time:.2f}s...", "INFO")
            await asyncio.sleep(wait_time)

    async def on_message(self, message):
        if message.channel.id != self.cfg.channel_id or message.author.id != self.MUDAE_ID:
            return

        content = message.content.lower()

        # Check for confirmation prompts (Both for KL and Scrap)
        if "do you want to spend" in content or "do you really want to give" in content:
            if "y/n" in content or "yes/no" in content:
                self.last_detected = "CONFIRM"
                self.response_event.set()
        
        # Success indicators
        elif any(x in content for x in ["rolls stacked", "kakera", "obtained", "scraps have been given"]):
            self.last_detected = "SUCCESS"
            self.response_event.set()
        
        # Error indicators
        elif "too many pins" in content or "release your duplicates" in content:
            self.last_detected = "PIN_ERROR"
            self.response_event.set()
        
        # arlp check
        elif "mudapins were released" in content:
            self.arlp_event.set()

if __name__ == "__main__":
    config = Config()
    bot = LootBot(config)
    try:
        bot.run(config.token)
    except Exception as e:
        print(f"{Fore.RED}[FATAL ERROR] {e}")
