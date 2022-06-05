import logging

import demjson3


class BandcampJSON:
    def __init__(self, body, debugging: bool = False):
        self.body = body
        self.json_data = []

        if debugging:
            logging.basicConfig(level=logging.DEBUG)

    def generate(self):
        """Grabbing needed data from the page"""
        self.get_pagedata()
        self.get_js()
        return self.json_data

    def get_pagedata(self):
        logging.debug(" Grab pagedata JSON..")
        pagedata = self.body.find('div', {'id': 'pagedata'})['data-blob']
        self.json_data.append(pagedata)

    def get_js(self):
        """Get <script> element containing the data we need and return the raw JS"""
        logging.debug(" Grabbing embedded scripts..")
        embedded_scripts_raw = [self.body.find("script", {"type": "application/ld+json"}).string]
        for script in self.body.find_all('script'):
            try:
                album_info = script['data-tralbum']
                embedded_scripts_raw.append(album_info)
            except:
                continue
        for script in embedded_scripts_raw:
            js_data = self.js_to_json(script)
            self.json_data.append(js_data)
            
    @staticmethod
    def list_all_albums(body, albums=True, tracks=True):
        albums = body.find_all('li', attrs={'class': 'music-grid-item'})
        albums = [a.find('a') for a in albums if a.find('a')]
        albums_url = [a['href'] for a in albums if a.has_attr('href')]
        if not albums:
            albums_url = [a for a in albums_url if not re.match(r'/album/.*', a)]
        if not tracks:
            albums_url = [a for a in albums_url if not re.match(r'/track/.*', a)]
        return albums_url

    @staticmethod
    def js_to_json(js_data):
        """Convert JavaScript dictionary to JSON"""
        logging.debug(" Converting JS to JSON..")
        # Decode with demjson first to reformat keys and lists
        decoded_js = demjson3.decode(js_data)
        # Encode to make valid JSON, add to list of JSON strings
        encoded_json = demjson3.encode(decoded_js)
        return demjson3.encode(decoded_js)
