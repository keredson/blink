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

## API
|Function|Description|Implemented|Works|
|--------|-----------|-----------|-----|
|`connect()`|Client login to the Blink Servers. | yes | yes | 
|`networks()`|Obtain information about the Blink networks defined for the logged in user. | yes | yes | 
|`sync_modules(network)`|Obtain information about the Blink Sync Modules on the given network. | yes | yes | 
|`arm(network)`|Arm the given network (start recording/reporting motion events). | yes | no | 
|`disarm(network)`|Disarm the given network (stop recording/reporting motion events. | yes | no | 
|`command_status()`|Get status info on the given command. | yes | unknown | 
|`homescreen()`|Return information displayed on the home screen of the mobile client. | yes | yes | 
|`events(network)`|Get events for a given network (sync module). | yes | yes | 
|`download_video(event)`|Get a video clip from the events list. | yes | yes | 
|`download_thumbnail(event)`|Get a thumbnail from the events list. | yes | no | 
|`cameras(network)`|Gets a list of cameras. | yes | yes | 
|`clients()`|Gets information about devices that have connected to the blink service. | yes | yes | 
|`regions()`|Gets information about supported regions. | yes | yes | 
|`health()`|Gets information about system health. | yes | yes | 
|`capture_video(camera)`|Captures a new video for a camera. | no |  | 
|`capture_thumbnail(camera)`|Captures a new thumbnail for a camera. | no |  | 
|`unwatched_videos()`|Gets a list of unwatched videos. | no |  | 
|`delete(video)`|Deletes a video. | no |  | 
