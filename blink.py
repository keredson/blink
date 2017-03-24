import io, json, os, requests, yaml


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
      self.networks.append(network)
    self._region = raw['region']
    self._authtoken = raw['authtoken']
  
  def homescreen(self):
    self._connect_if_needed()
    resp = requests.get(self._path('homescreen'), headers=self._auth_headers)
    return resp.json()
    
  def events(self, network_id, type='motion'):
    self._connect_if_needed()
    resp = requests.get(self._path('events/network/%s' % network_id), headers=self._auth_headers)
    events = resp.json()['event']
    if type: events = [e for e in events if e['type']=='motion']
    return events
  
  def download_video(self, event):
    '''
      returns the mp4 data as a file-like object
    '''
    self._connect_if_needed()
    resp = requests.get(self._path(event['video_url']), headers=self._auth_headers)
    return resp.content
    
  def download_thumbnail(self, event):
    '''
      returns the jpg data as a file-like object
      doesn't work - server returns 404
    '''
    self._connect_if_needed()
    thumbnail_url = self._path(event['video_url'][:-4] + '.jpg')
    resp = requests.get(thumbnail_url, headers=self._auth_headers)
    return resp.content
    
    
    
    
