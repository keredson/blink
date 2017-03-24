import json, unittest
from blink import Blink

class TestBlink(unittest.TestCase):

  def test_connect(self):
    b = Blink()
    self.assertFalse(b.connected)
    b.connect()
    self.assertTrue(b.connected)

  def test_homescreen(self):
    b = Blink()
    data = b.homescreen()
    self.assertTrue(data['account'] is not None)

  def test_events(self):
    b = Blink()
    b.connect()
    network_id = b.networks[0]['id']
    events = b.events(network_id)
    self.assertEqual(type(events), list)

  def test_download_video(self):
    b = Blink()
    b.connect()
    network_id = b.networks[0]['id']
    events = b.events(network_id)
    event = events[0]
    b.download_video(event)

  def _test_download_thumbnail(self):
    '''doesn't work'''
    b = Blink()
    b.connect()
    network_id = b.networks[0]['id']
    events = b.events(network_id)
    event = events[0]
    b.download_thumbnail(event)


if __name__ == '__main__':
    unittest.main()

