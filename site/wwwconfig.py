github = "https://github.com/jarro2783"

GAME_ROOT = '/home/pygame'
SERVERNAME = "AusNethack"
NETHACKDB = {"360" : "/home/nethack/game/stats.db"}
GAMELAUNCHDB = GAME_ROOT + '/users.db'
EMAIL = "jarro.2783@gmail.com"
SITE_GITHUB = github + "/ausnethack"
LAUNCHER_GITHUB = github + "/pygamelaunch"
NETHACK_GITHUB = github + "/nethack"
RECORDINGS_BACKEND = 's3'
S3_RECORDINGS_CONFIG = {
    'bucket' : 'ausnethack-recordings-compressed',
}
