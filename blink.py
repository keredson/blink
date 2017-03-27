from __future__ import print_function
import io, json, os, requests, sys, yaml
import dateutil.parser


__version__ = '0.2.0'



class Network(object):
  def __init__(self, **kwargs):
    for k,v in kwargs.items():
      setattr(self, k, v)
  def __repr__(self):
    return '<Network id=%s name=%s>' % (self.id, repr(self.name))


class Event(object):
  def __init__(self, **kwargs):
    for k,v in kwargs.items():
      setattr(self, k, v)
  def __repr__(self):
    return '<Event id=%s camera=%s at=%s>' % (self.id, repr(self.camera_name), repr(self.created_at))


class SyncModule(object):
  def __init__(self, **kwargs):
    for k,v in kwargs.items():
      setattr(self, k, v)
  def __repr__(self):
    return '<SyncModule %s>' % repr(self.__dict__)

class Camera(object):
  def __init__(self, **kwargs):
    for k,v in kwargs.items():
      setattr(self, k, v)
  def __repr__(self):
    return '<Camera id=%s name=%s>' % (self.id, repr(self.name))


class Blink(object):

  def __init__(self, email=None, password=None, config_fn=None, server='prod.immedia-semi.com'):
    if config_fn is None: config_fn = os.path.join(os.path.expanduser("~"), '.blinkconfig')
    self._authtoken = None
    self._email = None
    self._password = None
    self._server = server
    if email:
      self._email = email
    else:
      if os.path.isfile(config_fn):
        with open(config_fn) as f:
          config = yaml.load(f.read())
          if isinstance(config, dict):
            if len(config)==1:
              self._email, self._password = list(config.items())[0]
            if len(config)>1:
              raise Exception('Multiple email/passwords found in .blinkconfig.  Please specify which email to use.')
          else:
            raise Exception('File .blinkconfig must be a YAML dictionary.  Currently it is a YAML %s.' % type(config))
    if password:
      self._password = password
    elif self._email and not self._password:
      if os.path.isfile(config_fn):
        with open(config_fn) as f:
          config = yaml.load(f.read())
          if isinstance(config, dict):
            if self._email in config:
              self._password = config[self.email]
            else:
              raise Exception('File .blinkconfig does not contain a password for %s' % repr(self._email))
          else:
            raise Exception('File .blinkconfig must be a YAML dictionary.  Currently it is a YAML %s.' % type(config))
    if not self._email:
      raise Exception('Please specify an email address.')
    if not self._password:
      raise Exception('Please specify a password.')
  
  def _connect_if_needed(self):
    if not self._authtoken: self.connect()
    if not self.connected: raise Exception('Unable to connect.')
  
  @property
  def connected(self):
    return self._authtoken is not None
  
  @property
  def _auth_headers(self):
    return {'TOKEN_AUTH': self._authtoken['authtoken']}
    
  def _path(self, path):
    return 'https://%s/%s' % (self._server, path.lstrip('/'))
  
  def connect(self):
    headers = {
      'Content-Type': 'application/json',
      'Host': self._server,
    }
    data = {
      'email': self._email,
      'password': self._password,
      'client_specifier': 'Blink Home Security Camera Python API @ https://github.com/keredson/blink',
    }
    resp = requests.post(self._path('login'), json=data, headers=headers)
    if resp.status_code!=200:
      raise Exception(resp.json()['message'])
    raw = resp.json()
    self._networks_by_id = raw['networks']
    self.networks = []
    for network_id, network in self._networks_by_id.items():
      network = dict(network)
      network['id'] = network_id
      network = Network(**network)
      self.networks.append(network)
    self._region = raw['region']
    self._authtoken = raw['authtoken']
  
  def homescreen(self):
    '''
    Return information displayed on the home screen of the mobile client
    '''
    self._connect_if_needed()
    resp = requests.get(self._path('homescreen'), headers=self._auth_headers)
    return resp.json()
    
  def events(self, network, type='motion'):
    self._connect_if_needed()
    resp = requests.get(self._path('events/network/%s' % network.id), headers=self._auth_headers)
    events = resp.json()['event']
    if type: events = [e for e in events if e['type']=='motion']
    events = [Event(**event) for event in events]
    return events

  def cameras(self, network, type='motion'):
    self._connect_if_needed()
    resp = requests.get(self._path('network/%s/cameras' % network.id), headers=self._auth_headers)
    cameras = resp.json()['devicestatus']
    cameras = [Camera(**camera) for camera in cameras]
    return cameras
  
  def download_video(self, event):
    '''
      returns the mp4 data as a file-like object
    '''
    self._connect_if_needed()
    resp = requests.get(self._path(event.video_url), headers=self._auth_headers)
    return resp.content

  def download_thumbnail(self, event):
    '''
      returns the jpg data as a file-like object
      doesn't work - server returns 404
    '''
    self._connect_if_needed()
    thumbnail_url = self._path(event.video_url[:-4] + '.jpg')
    resp = requests.get(thumbnail_url, headers=self._auth_headers)
    return resp.content

  def sync_modules(self, network):
    '''
      Response: JSON response containing information about the known state of the Sync module, most notably if it is online
      Notes: Probably not strictly needed but checking result can verify that the sync module is online and will respond to requests to arm/disarm, etc.
    '''
    self._connect_if_needed()
    resp = requests.get(self._path('network/%s/syncmodules' % network.id), headers=self._auth_headers)
    return [SyncModule(**resp.json()['syncmodule'])]

  def arm(self, network):
    '''
      Arm the given network (start recording/reporting motion events)
      Response: JSON response containing information about the disarm command request, including the command/request ID
      Notes: When this call returns, it does not mean the disarm request is complete, the client must gather the request ID from the response and poll for the status of the command.
    '''
    self._connect_if_needed()
    resp = requests.get(self._path('network/%s/arm' % network.id), headers=self._auth_headers)
    return resp.json()

  def disarm(self, network):
    '''
      Disarm the given network (stop recording/reporting motion events)
      Response: JSON response containing information about the disarm command request, including the command/request ID
      Notes: When this call returns, it does not mean the disarm request is complete, the client must gather the request ID from the response and poll for the status of the command.
    '''
    self._connect_if_needed()
    resp = requests.get(self._path('network/%s/disarm' % network.id), headers=self._auth_headers)
    return resp.json()

  def command_status(self, network, command_id):
    '''
      Get status info on the given command
      Response: JSON response containing state information of the given command, most notably whether it has completed and was successful.
      Notes: After an arm/disarm command, the client appears to poll this URL every second or so until the response indicates the command is complete.
      Known Commands: lv_relay, arm, disarm, thumbnail, clip
    '''
    self._connect_if_needed()
    resp = requests.get(self._path('network/%s/command/%s' % (network.id, command_id)), headers=self._auth_headers)
    return resp.json()

  def clients(self):
    '''
      Request Gets information about devices that have connected to the blink service
      Response JSON response containing client information, including: type, name, connection time, user ID
    '''
    self._connect_if_needed()
    resp = requests.get(self._path('account/clients'), headers=self._auth_headers)
    return resp.json()

  def regions(self):
    '''
      Gets information about supported regions
    '''
    self._connect_if_needed()
    resp = requests.get(self._path('regions'), headers=self._auth_headers)
    return resp.json()

  def health(self):
    '''
      Gets information about system health
    '''
    self._connect_if_needed()
    resp = requests.get(self._path('health'), headers=self._auth_headers)
    return resp.json()



  # UTIL FUNCTIONS
    
  def archive(self, path):
    self._connect_if_needed()
    for network in self.networks:
      network_dir = os.path.join(path, network['name'])
      if not os.path.isdir(network_dir):
        os.mkdir(network_dir)

      already_downloaded = set()
      for fn in os.listdir(network_dir):
        if not fn.endswith('.mp4'): continue
        fn = fn[:-4]
        event_id = int(fn.split(' - ')[0])
        already_downloaded.add(event_id)

      events = self.events(network['id'])
      for event in events:
        if event['id'] in already_downloaded: continue
        when = dateutil.parser.parse(event['created_at'])
        event_fn = os.path.join(network_dir, '%s - %s @ %s.mp4' % (event['id'], event['camera_name'], when.strftime('%Y-%m-%d %I:%M:%S %p %Z')))
        print('Saving:', event_fn)
        mp4 = self.download_video(event)
        with open(event_fn,'w') as f:
          f.write(mp4)
          

def _main():        
  args = sys.argv[1:]
  if args[0]=='--archive':
    Blink().archive(args[1])
  
if __name__=='__main__':
  _main()
    
