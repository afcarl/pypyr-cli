"""tar.py unit tests."""
import logging
import pytest
from unittest.mock import call, patch
from pypyr.context import Context
from pypyr.errors import KeyInContextHasNoValueError, KeyNotInContextError
import pypyr.steps.pype as pype

# ------------------------ get_arguments --------------------------------------


def test_pype_get_arguments_all():
    """Parse all input from context."""
    context = Context({
        'pype': {
            'name': 'pipe name',
            'pipeArg': 'argument here',
            'useParentContext': 'parent context bool',
            'skipParse': 'skip parse',
            'raiseError': 'raise err'
        }
    })

    (pipeline_name,
     use_parent_context,
     pipe_arg,
     skip_parse,
     raise_error) = pype.get_arguments(context)

    assert pipeline_name == 'pipe name'
    assert use_parent_context == 'parent context bool'
    assert skip_parse == 'skip parse'
    assert raise_error == 'raise err'


def test_pype_get_arguments_defaults():
    """Parse all input from context and assign defaults where not specified."""
    context = Context({
        'pype': {
            'name': 'pipe name'
        }
    })

    (pipeline_name,
     use_parent_context,
     pipe_arg,
     skip_parse,
     raise_error) = pype.get_arguments(context)

    assert pipeline_name == 'pipe name'
    assert use_parent_context
    assert isinstance(use_parent_context, bool)
    assert skip_parse
    assert isinstance(skip_parse, bool)
    assert raise_error
    assert isinstance(raise_error, bool)


def test_pype_get_arguments_missing_pype():
    """Missing pype throw."""
    context = Context()

    with pytest.raises(KeyNotInContextError) as err_info:
        pype.get_arguments(context)

    assert repr(err_info.value) == ("KeyNotInContextError(\"context['pype'] "
                                    "doesn't exist. It must exist for "
                                    "pypyr.steps.pype.\",)")


def test_pype_get_arguments_missing_name():
    """Missing pype name throw."""
    context = Context({'pype': {}})

    with pytest.raises(KeyNotInContextError) as err_info:
        pype.get_arguments(context)

    assert repr(err_info.value) == (
        "KeyNotInContextError(\"pypyr.steps.pype missing 'name' in the 'pype' "
        "context item. You need to specify the pipeline name to run another "
        "pipeline.\",)")


def test_pype_get_arguments_name_empty():
    """Empty pype name throw."""
    context = Context({'pype': {'name': None}})

    with pytest.raises(KeyInContextHasNoValueError) as err_info:
        pype.get_arguments(context)

    assert repr(err_info.value) == (
        "KeyInContextHasNoValueError(\"pypyr.steps.pype ['pype']['name'] "
        "exists but is empty.\",)")
# ------------------------ get_arguments --------------------------------------

# ------------------------ run_step -------------------------------------------


@patch('pypyr.pipelinerunner.run_pipeline')
def test_pype_use_parent_context(mock_run_pipeline):
    """pype use_parent_context True."""
    context = Context({
        'pype': {
            'name': 'pipe name',
            'pipeArg': 'argument here',
            'useParentContext': True,
            'skipParse': True,
            'raiseError': True
        }
    })

    logger = logging.getLogger('pypyr.steps.pype')
    with patch.object(logger, 'info') as mock_logger_info:
        pype.run_step(context)

    mock_run_pipeline.assert_called_once_with(
        pipeline_name='pipe name',
        pipeline_context_input='argument here',
        context=context,
        parse_input=False)

    assert mock_logger_info.mock_calls == [
        call('pyping pipe name, using parent context.'),
        call('pyped pipe name.')]


@patch('pypyr.pipelinerunner.run_pipeline')
def test_pype_no_parent_context(mock_run_pipeline):
    """pype use_parent_context False."""
    context = Context({
        'pype': {
            'name': 'pipe name',
            'pipeArg': 'argument here',
            'useParentContext': False,
            'skipParse': True,
            'raiseError': True
        }
    })
    context.working_dir = 'arb/dir'

    logger = logging.getLogger('pypyr.steps.pype')
    with patch.object(logger, 'info') as mock_logger_info:
        pype.run_step(context)

    mock_run_pipeline.assert_called_once_with(
        pipeline_name='pipe name',
        pipeline_context_input='argument here',
        working_dir='arb/dir',
        parse_input=False)

    assert mock_logger_info.mock_calls == [
        call('pyping pipe name, without parent context.'),
        call('pyped pipe name.')]


@patch('pypyr.pipelinerunner.run_pipeline')
def test_pype_no_skip_parse(mock_run_pipeline):
    """pype use_parent_context False."""
    context = Context({
        'pype': {
            'name': 'pipe name',
            'pipeArg': 'argument here',
            'useParentContext': False,
            'skipParse': False,
            'raiseError': True
        }
    })
    context.working_dir = 'arb/dir'

    logger = logging.getLogger('pypyr.steps.pype')
    with patch.object(logger, 'info') as mock_logger_info:
        pype.run_step(context)

    mock_run_pipeline.assert_called_once_with(
        pipeline_name='pipe name',
        pipeline_context_input='argument here',
        working_dir='arb/dir',
        parse_input=True)

    assert mock_logger_info.mock_calls == [
        call('pyping pipe name, without parent context.'),
        call('pyped pipe name.')]


@patch('pypyr.pipelinerunner.run_pipeline')
def test_pype_no_pipe_arg(mock_run_pipeline):
    """pype use_parent_context False."""
    context = Context({
        'pype': {
            'name': 'pipe name',
            'pipeArg': None,
            'useParentContext': False,
            'skipParse': False,
            'raiseError': True
        }
    })
    context.working_dir = 'arb/dir'

    logger = logging.getLogger('pypyr.steps.pype')
    with patch.object(logger, 'info') as mock_logger_info:
        pype.run_step(context)

    mock_run_pipeline.assert_called_once_with(
        pipeline_name='pipe name',
        pipeline_context_input=None,
        working_dir='arb/dir',
        parse_input=True)

    assert mock_logger_info.mock_calls == [
        call('pyping pipe name, without parent context.'),
        call('pyped pipe name.')]


@patch('pypyr.pipelinerunner.run_pipeline', side_effect=RuntimeError('whoops'))
def test_pype_use_parent_context_no_swallow(mock_run_pipeline):
    """pype without swallowing error in child pipeline."""
    context = Context({
        'pype': {
            'name': 'pipe name',
            'pipeArg': 'argument here',
            'useParentContext': True,
            'skipParse': True,
            'raiseError': True
        }
    })

    logger = logging.getLogger('pypyr.steps.pype')
    with patch.object(logger, 'error') as mock_logger_error:
        with pytest.raises(RuntimeError) as err_info:
            pype.run_step(context)

        assert repr(err_info.value) == "RuntimeError('whoops',)"

    mock_run_pipeline.assert_called_once_with(
        pipeline_name='pipe name',
        pipeline_context_input='argument here',
        context=context,
        parse_input=False)

    mock_logger_error.assert_called_once_with(
        'Something went wrong pyping pipe name. RuntimeError: whoops')


@patch('pypyr.pipelinerunner.run_pipeline', side_effect=RuntimeError('whoops'))
def test_pype_use_parent_context_with_swallow(mock_run_pipeline):
    """pype swallowing error in child pipeline."""
    context = Context({
        'pype': {
            'name': 'pipe name',
            'pipeArg': 'argument here',
            'useParentContext': True,
            'skipParse': True,
            'raiseError': False
        }
    })

    logger = logging.getLogger('pypyr.steps.pype')
    with patch.object(logger, 'error') as mock_logger_error:
        pype.run_step(context)

    mock_run_pipeline.assert_called_once_with(
        pipeline_name='pipe name',
        pipeline_context_input='argument here',
        context=context,
        parse_input=False)

    mock_logger_error.assert_called_once_with(
        'Something went wrong pyping pipe name. RuntimeError: whoops')
    # ------------------------ run_step --------------------------------------
