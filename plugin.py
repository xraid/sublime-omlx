"""LLM plugin entry point. Sublime auto-loads this file at the package root."""
import sys

# kiss-reloader:
prefix = __spec__.parent + "."  # don't clear the base package
for module_name in [
    module_name
    for module_name in sys.modules
    if module_name.startswith(prefix) and module_name != __name__
]:
    del sys.modules[module_name]

# Imported names register the commands and event listener with the plugin host.
from .sublime_omlx.logging_setup import get_logger
from .sublime_omlx.chat_view import ChatViewEvents
from .sublime_omlx.commands import (
    SublimeOmlxCancelCommand,
    SublimeOmlxChooseModelCommand,
    SublimeOmlxChooseProviderCommand,
    SublimeOmlxClearChatCommand,
    SublimeOmlxOpenChatCommand,
    SublimeOmlxRenderLastResponseCommand,
    SublimeOmlxSendFileCommand,
    SublimeOmlxSendSelectionCommand,
    SublimeOmlxShowSecretStatusCommand,
    SublimeOmlxShowServerHealthCommand,
    SublimeOmlxShowStatusCommand,
    SublimeOmlxSubmitCommand,
)
from .sublime_omlx.text_commands import SublimeOmlxAppendCommand, SublimeOmlxNoopCommand


def plugin_loaded() -> None:
    get_logger().info("LLM loaded")
