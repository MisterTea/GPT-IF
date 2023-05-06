try:
    import unzip_requirements
except ImportError:
    pass

from gptif.dialogue_cache_server import app
from mangum import Mangum
from gptif.backend_utils import logger, metrics

handler = Mangum(app)

# Add logging
handler = logger.inject_lambda_context(handler, clear_state=True)
# Add metrics last to properly flush metrics.
handler = metrics.log_metrics(handler, capture_cold_start_metric=True)
