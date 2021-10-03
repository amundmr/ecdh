import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


setup(
  name = 'ecdh',         
  packages = ['ecdh'],   
  version = '0.1.0',     
  license='GNU General Public License v3.0',        
  description = 'ElectroChemical Data handler',
  long_description=README,
  author = 'Amund Raniseth',                   
  author_email = 'amund.raniseth@gmail.com',      
  url = 'https://github.com/amundmr/ecdh',   
  download_url = 'https://github.com/amundmr/ecdh/archive/refs/tags/v0.1.0.tar.gz',    # Remember to update this with new versions
  keywords = ['Electrochemical', 'battery', 'cell', 'datareader', 'dataplotter', 'reader', 'plotter'],
  install_requires=[
            'matplotlib',
            'numpy',
            'pandas',
            'toml',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
  entry_points={
        "console_scripts": [
            "ecdh=ecdh.__main__:main",
        ]
    },
)