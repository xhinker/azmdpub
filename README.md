# azmdpub

Writing and editing in Medium website is not only painful and also wasting of time on style wrangling. I am wondering if there is a way to write in Markdown file and then publish to Medium directly using Python. 

After some searches, no open source and free solution exists, not mention image uploading capability. So I decided to build one and open source it. This article is a summary of my solution. 

To publish a Markdown file to Medium site, I have to solve the following four problems: 

1. Translate Markdown to HTML string.
2. Extract meta info like `title` and `tags` from Markdown file.
3. The hardest part, upload images/GIFs to Medium server and update HTML image links. 
4. Post the HTML string to Medium site. 

Before moving on, Go to your medium home page to get the access token:

>Click your avatar -> Settings -> Security and apps -> Integration tokens

![](.publish_markdown_to_medium/2022-11-18-23-45-33.png)

The token will be used for Post uploading. 

## My solution - azmdpub 

Check out the code I post in github [azmdpub](https://github.com/xhinker/azmdpub). Pull the code, compile it, and start publishing your markdown files to Medium **with images**. 

The code works in Windows, Linux and MacOS. 

Here are steps to use it:

Step 1. Pull the code to your local machine

Step 2. Use `pyinstaller` to compile the code

Install `pyinstaller`:

```
pip install pyinstaller
```

Compile python code:
```
cd src/azmdpub
pyinstaller -F 'azmdpub.py' -n 'azmdpub'
```

Step 3. Now you shall see the executable file under `dist` folder, you can execute it like this:

```
./dist/azmdpub 'markdown_file.md'
```

The program will ask for `access token` in the first time use, then cache the token in file `~/medium.conf`.

The content in the `markdown_file.md` is like this:

```
---
title: Test markdown file
tags: ["tag1","tag2","tag3"]
---

# Test markdown file

This is a test markdown file

## Title2 

content content 
...

```

Note that the title and tags in the yaml meta section will be used during the uploading session.


If you still want to know how it works, please read on. 

## Problem #1. Translate Markdown to HTML string

With some researching and comparisons, I found package [markdown-it-py](https://github.com/executablebooks/markdown-it-py) is the best. The only problem is its confusing installation instruction from its readme file. 

Here is the working way to install the package with `pip`. 

Install `markdown-it-py`:
```bash
pip install markdown-it-py
```
Enable plugins: 
```bash
pip install mdit_py_plugins
```

Translate Markdown file to HTML string using the following code: 
```python
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.footnote import footnote_plugin
md = (
    MarkdownIt()
    .use(front_matter_plugin)
    .use(footnote_plugin)
    .enable('image')
    .enable('table')
)
with open(md_path,'r') as f:
    md_text = f.read()
```

## Problem #2. Extract meta info like `title` and `tags` from Markdown file

I can use Regex to extract the title and tags, but there is another module can do the extraction job. Module [`markdown`](https://pypi.org/project/Markdown/) can extract the meta information such as `title` and `tags` defined in the yaml header. 

```
---
title: Test markdown file
tags: ["tag1","tag2","tag3"]
---

# Test markdown file
```

Here is the code do the meta extraction work: 

```python 
import markdown 
with open(md_path,'r') as f:
    md_text = f.read()

md      = markdown.Markdown(extensions = ['meta'], output_format='html5')
html    = md.convert(md_text)
meta    = md.Meta
return {
    'title':meta['title'][0]
    ,'tags':meta['tags'][0]
}
```

## Problem #3. Upload images/GIFs to Medium server

I spent most of my time on implementing this feature, the post `boundary`  settings is confusing. With the help from this [solution](https://github.com/psf/requests/issues/1997#issuecomment-40031999) about `MultipartEncoder`, I managed to implement the image uploading function. The code support four image types:
1. image/jpeg
2. image/png
3. **image/gif**
4. image/tiff

Yes, Animated gifs are also supported. 

> Use your power for good

Here is the full function code, to run it, please check out the whole code file using the below link.

```python
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

    r = requests.post(
        post_image_url
        ,data = m.to_string()
        ,headers = image_up_headers
    )
    r_obj = json.loads(r.text)
    return r_obj['data']['url']
```
See full code file [here](https://github.com/xhinker/azmdpub/blob/main/src/azmdpub/azmdpub.py#L72). 

## Problem #4. Post the HTML string to Medium site

From the Medium's [official API document](https://github.com/Medium/medium-api-docs#33-posts) on Posting. You will see an `authorId` with double parentheses. 

```
POST https://api.medium.com/v1/users/{{authorId}}/posts
```

The `authorId` here is the user id or client id, you can fetch it with this code: 

```python
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
...
```
See full code [here](https://github.com/xhinker/azmdpub/blob/main/src/azmdpub/azmdpub.py#L52). The `{{}}` is unnecessary, you should remove it in the request call. 

Here is my implementation of blog Posting:

```python
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
```
See full code [here](https://github.com/xhinker/azmdpub/blob/main/src/azmdpub/azmdpub.py#L137).

## Last words

There are some other trivial processes I did not covered above, for example, the image URLs needed to be updated with the uploaded image links. These should be easy by using Python's string replacing functions.

This doc is written and edited with Markdown in VSCode. And post with `azmdpub` without any editing in Medium editor. Let me know if you are stuck or have any questions. Hope this tool enrich your writing experience. 