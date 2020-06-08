import json
import requests
from requests.auth import HTTPBasicAuth

from py.Secrets import ReadSecrets

from pprint import pprint

class PlotlyUtilities:

    @staticmethod
    def get_auth(username, api_key):
        return HTTPBasicAuth(username, api_key), {'Plotly-Client-Platform': 'python'}

    @staticmethod
    def get_pages(username, api_key, page_size=30):
        auth, headers = PlotlyUtilities.get_auth(username, api_key)
        url = 'https://api.plot.ly/v2/folders/all?user='+username+'&page_size='+str(page_size)
        response = requests.get(url, auth=auth, headers=headers)
        if response.status_code != 200:
            return
        page = json.loads(response.content)
        yield page
        while True:
            resource = page['children']['next']
            if not resource:
                break
            response = requests.get(resource, auth=auth, headers=headers)
            if response.status_code != 200:
                break
            page = json.loads(response.content)
            yield page

    @staticmethod
    def permanently_delete_files(username, api_key, page_size, filetype_to_delete):
        auth, headers = PlotlyUtilities.get_auth(username, api_key)

        for index, page in enumerate(PlotlyUtilities.get_pages(username, api_key, page_size)):
            print(f'== PAGE {index + 1} ==')
            for x in range(0, len(page['children']['results'])):
                fid = page['children']['results'][x]['fid']
                print(f'\t [ ] SEEKING FILE {fid}')
                res = requests.get('https://api.plot.ly/v2/files/' + fid, auth=auth, headers=headers)
                res.raise_for_status()

                if res.status_code == 200:
                    json_res = json.loads(res.content)
                    if json_res['filetype'] == filetype_to_delete:
                        print(f'\t [X] DELETING {fid} ({json_res["filetype"]})')
                        # move to trash
                        requests.post('https://api.plot.ly/v2/files/'+fid+'/trash', auth=auth, headers=headers)
                        # permanently delete
                        requests.delete('https://api.plot.ly/v2/files/'+fid+'/permanent_delete', auth=auth, headers=headers)

def clean(username, api_key):
    from multiprocessing import Pool

    pool = Pool(processes=10)
    pool.starmap(PlotlyUtilities.permanently_delete_files,
                 [
                     [username, api_key, 50, 'grid'],
                     [username, api_key, 50, 'plot'],
                     [username, api_key, 50, 'grid'],
                     [username, api_key, 50, 'plot'],
                     [username, api_key, 50, 'grid'],
                     [username, api_key, 50, 'plot'],
                 ])
    pool.close()
    pool.join()





def exercite():
    account = ReadSecrets('../secrets.json').read_if_necessary().secrets['plotly']
    pprint(account)
    clean(account['username'], account['apiKey'])

exercite()