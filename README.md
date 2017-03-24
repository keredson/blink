# Blink
Python API for the Blink Home Security Camera System

This is based off the documentation at: https://github.com/MattTW/BlinkMonitorProtocol

## Usage
```python
import blink
b = blink.Blink()
events = b.events()
an_event = events[0]
mp4_data = b.download_video(an_event)
```

This assumes you have a file `~/.blinkconfig` that looks like this:
```
me@somewhere.net: my_password
```
Alternatively, you can init Blink like so:
```
b = blink.Blink(email='me@somewhere.net', password='my_password')

