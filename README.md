# 💎 MudaLoot: High-Efficiency Kakera Looting Extension

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Self-Bot](https://img.shields.io/badge/Discord-Self--Bot-red.svg)](#disclaimer)

**MudaLoot** is a professional-grade automation extension designed specifically for the Mudae Discord Bot. It functions as a specialized high-efficiency "loot engine" to maximize your permanent Kakera gains and inventory rewards.

---

## 🔗 Relationship with MudaRemote
This project is an official extension for the **MudaRemote** ecosystem. While [MudaRemote](https://github.com/misutesu-desu/MudaRemote) manages your daily rolls, snipes, and character wishlist, **MudaLoot** is the dedicated tool for spending your Kakera on `$kl` (Kakera Loot) cycles.

---

## ✨ Key Features
- **Automated $kl Engine:** Continuously sends `$kl` commands based on your specified Kakera amount.
- **Smart Confirmation:** Automatically detects and responds to Mudae's "y/n" spend confirmations.
- **Auto-Inventory Management:** Detects "Too many pins" errors and executes `$arlp` to release duplicate pins automatically.
- **Sync Logic:** Employs `asyncio.Event` synchronization to ensure the bot waits for Mudae's response before proceeding with the cycle.
- **Anti-Detection Jitter:** Randomizes cooldowns (default 30-32s) to mimic human behavior.
- **Professional Logging:** Clean, color-coded console output with precise timestamps.

---

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/misutesu-desu/MudaLoot.git
   cd MudaLoot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration:**
- Edit `config.json` with your **Discord Token**, **Target Channel ID**, and preferred **KL Amount**.

4. **Launch:**
   ```bash
   python main.py
   ```

---

## ⚙️ Configuration (config.json)
| Key | Description |
|-----|-------------|
| `token` | Your Discord account token (Self-bot). |
| `target_channel_id` | The ID of the channel where the bot will roll `$kl`. |
| `kl_amount` | The Kakera amount to spend per command (e.g., "12000"). |
| `min_cooldown` | The minimum wait time between loot cycles (in seconds). |
| `max_cooldown` | The maximum wait time between loot cycles (in seconds). |

---

## ⚠️ Disclaimer
**MudaLoot** is a self-bot. Using self-bots on Discord violates their **Terms of Service**.
- Using this tool carries a high risk of account suspension or permanent ban.
- The developers are not responsible for any actions taken by Discord against your account.
- **Use this tool at your own risk.**

---
*Developed by [misutesu-desu] - Part of the [MudaRemote](https://github.com/misutesu-desu/MudaRemote) ecosystem.*
