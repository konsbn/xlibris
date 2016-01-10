from setuptools import setup

setup(name = 'xlibris',
      version = '0.1',
      description = 'A very simple console based library management system written in Python',
      url = 'https://github.com/konsbn/xlibris',
      author = 'Shubham Bhushan',
      keywords = ['books', 'library', 'isbn'],
      author_email = 'shubphotons@gmail.com',
      license = 'MIT',
      packages = ['xlibris'],
      install_requires = ['tabulate', 'tqdm', 'isbntools','pyfiglet', 'tinydb'],
      scripts = ['bin/xLibris'],
      zip_safe = False)
