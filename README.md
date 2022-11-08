# azmdpub

A tool can publish markdown file to medium.com. Key features:

* Automatically translate markdown file to html;
* Upload images to medium server, the first tool in this planet provides the upload image feature.

## How to use it

Step 1. Pull the code to your local machine

Step 2. Use `pyinstaller` to compile the code

```
cd src/azmdpub
pyinstaller -F 'azmdpub.py' -n 'azmdpub'
```

Step 3. Now you shall see the executable file under dist folder. 

```
./dist/azmdpub 'markdown_file.md'
```

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

## How to get Medium's access token. 

Go to your medium home page. 

Click your avatar -> Settings -> Security and apps -> Integration tokens

## References

This is a Python implementation of [Medium's official API documentation](https://github.com/Medium/medium-api-docs)