#   MIT License

#   Copyright (c) 2023 andshrew
#   https://github.com/andshrew/Discord-Message-Python

#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:

#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.

#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.

"""Create and send Discord webhook messages.

This module enables you to create and send simple Discord webhook messages.
By default if a message fails to send (ie. server error), the message is added to
a "queue" by saving it as a file. This queue can be processed and re-sent at a later
time.

Typical usage example:

    discord_webhook_url = 'https://discord.com/webhook'
    discord_message = DiscordMessage(content='My first simple Discord message!', webhook_url=discord_webhook_url)
    discord_message.send_message()

    discord_message = DiscordMessage(webhook_url=discord_webhook_url)
    embed = DiscordMessageEmbed(title='Hello World', message='My first Discord embed!')
    discord_message.add_embed(embed.get_embed())
    discord_message.send_message()
"""

import datetime
import json
import logging
from pathlib import Path
import random
import requests

class Discord:
    """Base class handling sending and saving Discord messages.

    This base class contains the methods for sending and saving DiscordMessage objects.

    This class should not be directly invoked and instead should be accessed via the child
    classes:
        DiscordMessage
        DiscordQueue

    Attributes:
        queue_path: Path where the message can be saved as a file.
                    Default is a directory named 'discord' in the current working directory
                    Specify None or '' to disable
        queue_suffix: String to append to the generated file name of any saved files
                      Default is 'queued-message'
                      Example: 2023-02-07T17.04.210686-24759-queued-message.json
    """
    def __init__(self, queue_path='discord', queue_suffix='queued-message') -> None:
        self.queue_path = queue_path
        self.queue_suffix = queue_suffix
        if self.queue_suffix is None:
            self.queue_suffix = ''
    
    def send_message(self, message, webhook_url='disabled', queue_message=False):
        """Send the message_object attribute of a DiscordMessage object to Discord.

        The message_object attribute of a DiscordMessage object is coverted into a JSON string and
        sent in a HTTP POST request to the Discord servers.
        
        If the message cannot be sent (ie. due to an error on the receiving server) then the message
        can be saved as a file in the directory specified in attribute "queue_path".
        The default location is a directory named 'discord' in the current working directory.

        If the "webhook_url" attribute is set to 'disabled' the method will discard the message.

        Args:
            message: The message_object attribute of a DiscordMessage object
                     Alternatively a list object of the same structure (eg. when sending a message
                     which was previously saved as a file)
            webhook_url: The Discord webhook url this message will be sent to. 
                         Default is 'disabled'
            queue_message: If 'True' the method will not attempt to save the message as a file.
                           This is useful when attempting to re-send a message which has previously
                           been saved as a file (ie. there is no need to save it again should it
                           fail to send again).
                           Default is 'False'

        Returns:
            True: The message has been successfully sent.
                  The message was not sent because attribute "webhook_url" is set to 'disabled'.
            False: The message could not be parsed into a JSON string.
                   The message could not be sent and could not be saved as a file.
                   The message could not be sent and will not be saved as a file (attribute "queue_path" is None or '')
        """

        if webhook_url == 'disabled':
            logger.debug(f'No Discord message will be sent as webhook_url is {webhook_url}')
            return True

        try:
            message_json = json.dumps(message)
        except TypeError as ex:
            logger.error(f'Unable to parse message into a JSON string: {ex.args}')
            return False

        try:
            result = requests.post(webhook_url, data=message_json,
                                headers={'Content-Type': 'application/json; charset=utf-8'})  
        except requests.exceptions.RequestException as ex:
            logger.error(f'Requests protocol exception: {ex.args}')

        if not result.status_code // 100 == 2:
            logger.error(f'Requests HTTP error: {result.status_code}')
            if not queue_message:
                save_result = self._save_message(message=message, webhook_url=webhook_url)
                if save_result == False:
                    return False
            return False
        return True

    def _save_message(self, message, webhook_url):
        """Save the message_object attribute of a DiscordMessage object to a file.

        The message_object attribute of a DiscordMessage object is coverted into a JSON string and
        saved as a file in directory defined in the "queue_path" attribute of this class.

        The default location is a directory named 'discord' in the current
        working directory. If the attribute is None or '' then the message will not be saved
        as a file.

        If the message contains an "embed" then the timestamp attribute is added containing the current time.
        This adds a visual indication to the message once it has been sent to Discord that the message has
        been delayed from when it was initially sent.

        The "webhook_url" is appended to the "message" object so that it is included in the JSON
        string which is saved as a file. This enables the message to be sent at a later time, but this
        attribute must be removed from the object when it is loaded back in before it can be sent to
        Discord.

        Args:
            message: The message_object attribute of a DiscordMessage object.
                     Alternatively a list object of the same structure (eg. when sending a message
                     which was previously saved as a file).
            webhook_url: The Discord webhook url this message will be sent to.

        Returns:
            True: The message has been successfully saved as a file.
                  The message was not saved because attribute "queue_path" is set to None or ''.
            False: The message could not be parsed into a JSON string.
                   The message could not be saved as a file.
        """
        if self.queue_path is None or self.queue_path == '':
            logger.debug('Saving Discord messages to the queue is disabled')
            return False

        file_name = f'{datetime.datetime.utcnow().strftime("%Y-%m-%dT%H.%M.%f%Z")}-{random.randint(1000,50000)}-{self.queue_suffix}.json'
        message_path = Path(self.queue_path).joinpath(file_name)
        logger.info(f'Saving message to: {message_path}')
        try:    
            Path(self.queue_path).mkdir(parents=True, exist_ok=True)
        except NotADirectoryError as ex:
            logger.error(f'Unable to create message queue path {self.queue_path}: {ex.args}')
            return False

        timestamp = datetime.datetime.utcnow().isoformat()
        if 'embeds' in message:
            for embed in message["embeds"]:
                embed["timestamp"] = f'{timestamp}'

        message["webhook_url"] = webhook_url

        if Path(message_path).exists():
            logger.error('A file at path "{message_path}" already exists. Message cannot be saved to the queue')
            return False

        try:
            with open(message_path, "w", encoding="utf-8") as output_file:
                json.dump(message, output_file, indent=4)
        except TypeError as ex:
            logger.error(f'Unable to parse message into a JSON string: {ex.args}')
            return False
        except Exception as ex:
            logger.error(f'Unable to save message to queue: {ex.args}')
            return False
        return True

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    print('https://github.com/andshrew/Discord-Message-Python')