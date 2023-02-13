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

import json
import logging
from pathlib import Path

from discord_andshrew.discord import Discord

class DiscordQueue(Discord):
    """Send messages which have been saved as files in the queue.

    Contains methods for processing and sending messages which were previously saved
    as files in the queue directory. The file is deleted if the message is successfully
    sent.

    Attributes:
        queue_path: Path where the messages have been saved as a file.
                    Default is a directory named 'discord' in the current working directory
        queue_suffix: String to append to the file name when searching for saved files.
                      This enables messages from different applications to be saved in the same directory 
                      and potentially re-sent at a later time via seperate handlers.
                      Default is 'queued-message'
                      Example: *queued-message.json
    """
    def __init__(self, queue_path='discord', queue_suffix='queued-message') -> None:
        super().__init__(queue_path, queue_suffix)

    def send_queue(self):
        """Send all messages in the queue

        Send all messages which have been saved as files in the directory specified in
        the attribute "queue_path".

        File selection is limited to files with a suffix matching attribute "queue_suffix"

        The file is deleted if it is successfully sent to the Discord server.

        Returns:
            True: The message queue has been processed
            False: Attribute "queue_path" is not configured
                   Unable to get files from "queue_path"
        """
        logger.debug('Processing message queue')
        logger.debug(f'Queue path: {self.queue_path}')
        logger.debug(f'Queue suffix: {self.queue_suffix}')

        if self.queue_path is None or self.queue_path == '':
            logger.error('No Discord queue path configured')
            return True

        try:
            message_files = list(Path(self.queue_path).glob(f'*{self.queue_suffix}.json'))
        except Exception:
            return False

        logger.debug(f'Messages in queue: {len(message_files)}')
        for file in message_files:
            with open(file.absolute(), encoding='utf-8') as f:
                message = json.load(f)
            
            webhook_url = message['webhook_url']
            # Remove the webhook_url from the object
            message.pop('webhook_url', None)
            if self.send_message(message=message, webhook_url=webhook_url, queue_message=True):
                try:
                    file.unlink()
                    logger.debug(f'Deleted file: {file.absolute()}')
                except Exception as ex:
                    logger.error(f'Unable to delete {file.absolute()}: {ex.args}')

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    print('https://github.com/andshrew/Discord-Message-Python')