# Simple Discord Webhook Messages

This package enables the creation and sending of simple Discord webhook messages. It can additionally save messages which have failed to send as a file, enabling the creation of a message queue which can be re-sent at a later time.

This was originally created to the requirements of my own personal projects and as such is not an exhaustive implementation of Discords webhook capabilities (see [Limitations](#limitations)).

## Installation
```
pip install discord-andshrew
```
## Typical Usage

Create a `DiscordMessage` object specifying your Discord webhook URL. By default, should any messages fail to send they will be saved as a file in a directory named `discord` within the current working directory. To disable this behaviour set `queue_path` to `''` or `None`. Alternatively set to a path of your choice.

For more complex messages create and attach up to 10 `DiscordMessageEmbed` objects to your message.

## Limitations

Text field limits are not validated. You should verify against the [Discord Limits](https://discord.com/developers/docs/resources/channel#embed-object-embed-limits) specification and implement checks within your application as required.

## Usage Examples

### Simple Text Message

```python
from discord_andshrew import message as discord

webhook_url = 'https://discord.com/api/webhooks/...'
message = discord.DiscordMessage(webhook_url=webhook_url)
message.content = 'Simple message example!'
message.send_message()
```
![Simple Plain Text Message](docs/images/example_simple_message.png)

### Message with Single Embed

```python
from discord_andshrew import message as discord

webhook_url = 'https://discord.com/api/webhooks/...'
message = discord.DiscordMessage(webhook_url=webhook_url)
embed = discord.DiscordMessageEmbed(
        title="Testing Testing",
        message="This is a test message!"
    )
message.add_embed(embed.get_embed())
message.send_message()
```
![Message with Single Embed Example](docs/images/example_single_embed.png)

### Message with Multiple Embeds and Fields

```python
from discord_andshrew import message as discord

webhook_url = 'https://discord.com/api/webhooks/...'
message = discord.DiscordMessage(webhook_url=webhook_url)

embed = discord.DiscordMessageEmbed(
        title="First Embed",
        message="This is the first example embed!"
    )
embed.add_field(
        title='Field 1',
        message='These fields are on the same row',
        inline=True
    )
embed.add_field(
    title='Field 2',
    message='Because `inline` is `True`',
    inline=True
)
embed.add_field(
    title='Field 3',
    message='Up to three in a row!\n_But sometimes limited to 2..._',
    inline=True
)
message.add_embed(embed.get_embed())

embed = discord.DiscordMessageEmbed(
        title="Second Embed",
        message="This is the second example embed!\n\nYou can add up to 10 embeds per message :eyes:"
    )
embed.add_field(
        title='Field 1',
        message='These fields are on their own row',
    )
embed.add_field(
    title='Field 2',
    message='Because `inline` is `False`',
)
embed.add_field(
    title='Field 3',
    message='Add up to 25 fields per embed',
)
message.add_embed(embed.get_embed())

message.send_message()
```
![Message with Multiple Embeds and Fields](docs/images/example_multiple_embeds.png)

## Message Queue

By default, should any messages fail to send they will be saved as a file in a directory named `discord` within the current working directory. To disable this behaviour when creating your `DiscordMessage` object set `queue_path` to `''` or `None`. Alternatively set to a path of your choice.

You can manually invoke saving a message as a file by calling `save_message()` on your `DiscordMessage` object.

When a message is saved to a file:

* If the message includes an embed then a timestamp property is appended. This is to give a visual indication within the Discord client of the original sending time for the message.
* The `webhook_url` is appended as a new property on the messages JSON. This enables the queue sending process to re-send the message to the correct URL.

The contents of a saved message will look similar to:

```json
{
    "content": null,
    "embeds": [
        {
            "title": "Testing Testing",
            "description": "This is a test message!",
            "timestamp": "2023-02-13T20:02:19.835651"
        }
    ],
    "webhook_url": "https://discord.com/api/webhooks/..."
}
```
![Queue Message](docs/images/example_queue_message.png)

> ⚠️ **Note** <br>As a result of adding the `webhook_url` property the saved JSON is not suitable for sending directly to Discords servers, because it is no longer complaint with their specification. Before attempting to re-send this JSON the `webhook_url` property must be removed.

Message files are deleted once they have been successfully sent by the queue sending process.

### Examples for Sending Queued Messages

#### Default Parameters

```python
from discord_andshrew import queue

queue.DiscordQueue().send_queue()
```

#### Custom Queue Path

```python
from discord_andshrew import queue

queue.DiscordQueue(queue_path='my_custom_queue_path').send_queue()
```