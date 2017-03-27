![image](https://cloud.githubusercontent.com/assets/2049665/24316082/58e34c7e-10b9-11e7-93fa-88ca46f13d46.png)

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
```

## Archiving Video
Blink eventually deletes old video clips.  If you want to archive your videos locally, run:

```
$ python -m blink --archive path/to/archive_dir
```

Typically this would be put into a cron job.
