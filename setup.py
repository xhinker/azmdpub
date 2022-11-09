from setuptools import setup,find_packages

setup(
    name='azmdpub',
    version='1.221107.1',
    license='MIT License',
    author="Andrew Zhu",
    author_email='xhinker@hotmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/xhinker/azmdpub',
    keywords='markdown medium',
    install_requires=[
        'markdown'
        ,'markdown-it-py'
        ,'mdit_py_plugins'
    ],
)