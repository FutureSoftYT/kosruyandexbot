from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
YADISK_TOKEN = env.str("YADISK_TOKEN")  # Забираем значение типа str
