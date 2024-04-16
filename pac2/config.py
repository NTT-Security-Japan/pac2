import os

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.path.dirname(__file__), "data.db")
    # C2_URL = os.getenv("PAC2_URL", "https://[your-domain-comes-here]")
    SECRET_KEY = "hello_from_powerautomatec2"
    SET_APPROVE_ACTION = True
    SLEEP_TIME = 60
    JITTER = 10
    DROPBOX_LOG_PATH = os.path.abspath(os.path.join(__file__, "..","app", "log"))
    DROPBOX_MOUNT_PATH = os.path.abspath(os.path.join(__file__, "..", "..", "mount", "dropbox", "Dropbox"))
    DROPBOX_PAC2_ROOT = os.path.join(DROPBOX_MOUNT_PATH, "pac2")

def print_config(cls):
    for attribute in dir(cls):
        if not attribute.startswith('__') and not callable(getattr(cls, attribute)):
            value = getattr(cls, attribute)
            print(f"{attribute} = {value}")

if __name__ == "__main__":
    print_config(Config)