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

#from discord import Discord
from discord_andshrew.discord import Discord

class DiscordMessage(Discord):
    """Creates a simple Discord webhook message.

    Creates a simple Discord webhook message with support for adding additional "embeds".
    The message can optionally be saved as a file to be sent at a later time.

    Attributes:
        content: Text to be included in the message.
                 Limited Markdown support.
        webhook_url: The Discord webhook url this message will be sent to. 
                     Default is 'disabled'
        queue_path: Path where the message can be saved as a file.
                    Default is a directory named 'discord' in the current working directory
                    Specify None or '' to disable
        queue_suffix: String to append to the generated file name of any saved files
                      Default is 'queued-message'
                      Example: 2023-02-07T17.04.210686-24759-queued-message.json
        embeds: List of "embeds" to include with the message.
                Limit of 10
    """

    def __init__(self, content=None, webhook_url='disabled', queue_path='discord',
                 queue_suffix='queued-message'):
        self.content = content
        self.webhook_url = webhook_url
        self.embeds = []
        super().__init__(queue_path=queue_path, queue_suffix=queue_suffix)

    def _build_message(self):
        """Internal method to build the Discord webhook message.

        Build the 'message_object' attribute, which is a list that resembles the format
        of a Discord webhook message. This attribute can then be parsed into JSON.
        """
        self.message_object = {}
        self.message_object['content'] = self.content
        if len(self.embeds) > 0:
            self.message_object['embeds'] = self.embeds

    def add_embed(self, embed):
        """Add a DiscordMessageEmbed object to this message.

        Add up to 10 DiscordMessageEmbed objects to this message.

        Args:
            embed: A DiscordMessageEmbed object
        """
        embed_limit = 10
        if len(self.embeds) < embed_limit:
            self.embeds.append(embed)
        else:
            logger.error(f'Cannot add more than {embed_limit} embeds to this message')
        return self

    def get_json(self):
        """Parse this message into a Discoard webhook JSON string.

        Returns:
            A string containing the Discord webhook JSON for the message.
            For example:

            '{"content": null, "embeds": [{"title": "Hello World", "description": "My first Discord embed!"}]}'
        """
        self._build_message()
        try:
            message_json = json.dumps(self.message_object)
        except TypeError as ex:
            logger.error(f'Unable to parse message into JSON: {ex.args}')
            logger.debug(self.message_object)
            return
        logger.debug(message_json)
        return message_json

    def save_message(self):
        """Save this message as JSON to a file.

        The message is saved as a file in directory "queue_path" defined when this object
        was created. The default location is a directory named 'discord' in the current
        working directory.
        
        The "webhook_url" is included in the JSON to enable the message to be sent at a later
        time.
        """
        self._build_message()
        Discord._save_message(self, message=self.message_object, webhook_url=self.webhook_url)
    
    def send_message(self):
        """Send the message to Discord.

        The message is sent to the Discord servers. If the message cannot be sent (ie. due to
        an error on the receiving server) then the message will be saved as a file in the directory
        "queue_path". The default location is a directory named 'discord' in the current
        working directory.

        If the "webhook_url" attribute is set to "disabled" the sending method will discard the message.
        """
        self._build_message()
        Discord.send_message(self, message=self.message_object, webhook_url=self.webhook_url)

class DiscordMessageEmbed:
    """Create an "embed" for attaching to a DiscordMessage object

    An "embed" is a standalone message which can be included in a Discord webhook message.
    It provides additional formatting options over the basic text message which is included in a
    standard message.

    10 DiscordMessageEmbed objects can be attached to a single DiscordMessage object.

    Attributes:
        title: Title for the embed.
        url: URL that the title will link to.
            * Caution * if "title" is not set then "url" will not be visible in the final message
        message: Text to include in the embed. Limited Markdown support.
        color: Colour to be displayed on left border of embed.
            Must be provided as decimal value.
            https://www.spycolor.com
        footer: Text to include at the footer of the embed
    """

    def __init__(self, title=None, url=None, message=None, colour=None, footer=None):
        self.title = title
        self.url = url
        self.description = message
        self.color = colour
        self.footer = footer
        self.fields = []

    def add_field(self, title, message, inline=False):
        """Add a field to the embed

        A field is a table like display containing a title and message. Up to 25 fields
        can be added to an embed.

        By default each field will be displayed on its own row, but this can be
        changed by setting "inline" to True. With this set up to 3 fields can display
        on a single row (but this can change and be limited to 2 per row depending on
        what other features are being used by the Discord message).

        You can set both the "title" and "message" to '' along with "inline" to True to
        potentially do some creative positioning of fields.

        Args:
            title: Title for the field. Limited Markdown support.
            message: Text message for the field. Limited Markdown support.
            inline: The field can display on the same row as another field.
                    Requires the next (or previous) field to also have this set as True.

        """
        field_limit = 25
        if len(self.fields) < field_limit:
            self.fields.append({
            'name': title,
            'value': message,
            'inline': inline
        })
        else:
            logger.error(f'Cannot add more than {field_limit} embeds to this message')
        
        return self

    def _build_embed(self):
        """Internal method to build the embed for the Discord webhook message.

        Build the 'message_object' attribute, which is a dict that resembles the format
        of an embed in a Discord webhook message.

        Raises:
            ValueError: An embed must have either a title, description, or a fields object
        """
        self.message_object = {}
        if (len(self.fields) == 0) and (self.title == None and self.description == None):
            raise ValueError('An embed must have either a title, description, or a fields object')
        if not self.title == None:
            self.message_object['title'] = self.title
        if not self.url == None:
            self.message_object['url'] = self.url
            if self.title == None:
                logger.warning('The URL in this embed will be only accessible if the title property is also set')
        if not self.description == None:
            self.message_object['description'] = self.description
        if not self.color == None:
            self.message_object['color'] = self.color
        if not self.footer == None:
            self.message_object['footer'] = {'text': self.footer}
        if len(self.fields) > 0:
            self.message_object['fields'] = self.fields
        return self.message_object

    def get_embed(self):
        """Add the embed to a DiscordMessage object

        Prepares the embed object for adding to a DiscordMessage object

        Returns:
            A dict object that resembles the format of an embed in a Discord webhook message
        """
        self._build_embed()
        return self.message_object

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    print('https://github.com/andshrew/Discord-Message-Python')