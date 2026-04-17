import sqlite3
import os

print("Шлях:", os.getcwd())

conn = sqlite3.connect("bot.db")
print("БАЗА СТВОРЕНА")