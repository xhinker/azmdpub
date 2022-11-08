# https://github.com/Medium/medium-api-docs
import requests
from requests_toolbelt import MultipartEncoder
import json

import markdown 
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.footnote import footnote_plugin

import re

from pathlib import Path

class azmdpub:
    def __init__(self,token=None) -> None:
        '''
        The __init__ will initialize access_token, base_url, default http headers 
        and fetch the client_id or user_id for future use. 
        '''
        home_path = Path.home()
        conf_path = home_path / '.medium.conf'
        if token:
            self.access_token   = token
            print('update token in conf file')
            with open(conf_path,'w') as f:
                f.write(self.access_token)
        else:
            # check if the existence of .medium.conf file
            # if yes, load token from the conf file
            if Path.exists(conf_path):
                with open(conf_path,'r') as f:
                    self.access_token = f.read()
            else:
                # if not, pop console ask token and save to .medium.conf file
                print('Please provide your Medium access-token:')
                self.access_token = input()
                with open(conf_path,'w') as f:
                    f.write(self.access_token)
                print(f'Your token is saved in file:{str(conf_path)}')

        self.base_url       = "https://api.medium.com/v1/"
        self.headers = {
            'Authorization': "Bearer " + self.access_token
            ,'Content-Type': 'application/json'
            ,'Accept': 'application/json'
            ,'Accept-Charset': 'utf-8'
        }
        try:
            r = requests.get(self.base_url+'me',headers=self.headers)
            self.client_obj = json.loads(r.text)
            self.client_id = self.client_obj['data']['id']
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def md_to_html_meta(self,md_path):
        '''
        The markdown convert can extract meta info from markdown file,but not able to extract the code block
        This why md_to_html function will be used to convert markdown string to html. 
        '''
        with open(md_path,'r') as f:
            md_text = f.read()

        md      = markdown.Markdown(extensions = ['meta'], output_format='html5')
        html    = md.convert(md_text)
        meta    = md.Meta
        return {
            'title':meta['title'][0]
            ,'tags':meta['tags'][0]
        }
    
    def upload_img(self,img_path):
        '''
        Upload one image to medium server
        '''
        post_image_url = "https://api.medium.com/v1/images"
        img_type = img_path.split('.')[-1]

        files = {
            'image': (
                img_path
                ,open(img_path,'rb')
                ,f'image/{img_type}'
            )
        }

        m = MultipartEncoder(files, boundary='FormBoundaryXYZ')

        image_up_headers = {
            'Authorization':    "Bearer " + self.access_token
            ,'Content-Type':    m.content_type
            ,'Accept':          'application/json'
            ,'Accept-Charset':  'utf-8'
        }

        r = requests.post(post_image_url, data=m.to_string(),headers=image_up_headers)
        r_obj = json.loads(r.text)
        return r_obj['data']['url']
    
    def upload_all_imgs(self,md_text) -> str:
        # extract image path from the md text
        re_pattern = r'\!\[.*?\]\((.*?)\)'
        result = re.findall(re_pattern,md_text)
        # loop and upload image to medium server, return file_path to url dictionary
        img_dict = {}
        for img in result:
            img_dict[img] = self.upload_img(img)
        # replace the md string's image path with uploaded url
        for key in img_dict:
            md_text = md_text.replace(key,img_dict[key])

        return md_text
    
    def md_to_html(self,md_path):
        '''
        This function will convert markdown file to html string use markdown-it-py

        Medium do not support table and embedded html code.

        By `.enable('image')`, ![](image_path) will be convert to <img> instead of <a>
        '''
        md = (
            MarkdownIt()
            .use(front_matter_plugin)
            .use(footnote_plugin)
            .enable('image')
            .enable('table')
        )
        with open(md_path,'r') as f:
            md_text = f.read()
        
        md_text = self.upload_all_imgs(md_text)
        
        html_str = md.render(md_text)
        return html_str
    
    def pub_post(self,md_path,status='draft'):
        
        post_url = f"{self.base_url}/users/{self.client_id}/posts"

        post_obj = self.md_to_html_meta(md_path)
        html_content = self.md_to_html(md_path)

        post_json = {
            "title": post_obj['title'],
            "contentFormat": "html",
            "content": html_content,
            "tags": json.loads(post_obj['tags']),
            "publishStatus": status
        }

        r = requests.post(post_url,json=post_json,headers=self.headers)
        print(r.text)

def prepare_env(token):
    '''
    Call this function to persist token in .medium.conf file
    '''
    from pathlib import Path
    home_path = Path.home()
    conf_path = home_path / ".medium.conf"
    with open(conf_path,'w') as f:
        f.write(token)
    print('token set done')

if __name__== "__main__":
    import argparse
    import sys
    my_parser = argparse.ArgumentParser(description="Publish Markdown file to Medium")

    my_parser.add_argument(
        'md_path'
        ,type=str
    )

    my_parser.add_argument(
        '-s'
        ,'--status'
        ,type=str
    )

    my_parser.add_argument(
        '-at'
        ,'--access_token'
        ,type=str
    )

    args = my_parser.parse_args()

    md_path         = args.md_path
    status          = args.status
    access_token    = args.access_token

    if access_token:
        prepare_env(access_token)
    azmdpub = azmdpub()

    if status:
        azmdpub.pub_post(md_path,status=status)
    else:
        azmdpub.pub_post(md_path,status='draft')

