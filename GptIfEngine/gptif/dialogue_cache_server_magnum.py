from gptif.dialogue_cache_server import app
from mangum import Mangum

handler = Mangum(app)
