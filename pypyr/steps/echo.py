"""Step that echos simple input back to logger."""
import logging

# logger means the log level will be set correctly
logger = logging.getLogger(__name__)


def run_step(context):
    """Simple echo. Outputs context['echoMe'].

    Args:
        context: dictionary-like. context is mandatory.
                 context must contain key 'echoMe'
                 context['echoMe'] will echo the value to logger.
                 This logger could well be stdout.

    When you execute the pipeline, it should look something like this:
    pypyr [name here] 'echoMe=test', assuming a keyvaluepair context parser.
    """
    logger.debug("started")

    assert context, ("context must be set for echo. Did you set "
                     "'echoMe=text here'?")

    context.assert_key_exists('echoMe', __name__)

    if isinstance(context['echoMe'], str):
        val = context.get_formatted('echoMe')
    else:
        val = context['echoMe']

    logger.info(val)

    logger.debug("done")
