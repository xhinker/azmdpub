# azmdpub

A tool can publish markdown file to medium.com

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

## How to get Medium's access token. 

Go to you medium home page. 

Click your avatar -> Settings -> Security and apps -> Integration tokens
