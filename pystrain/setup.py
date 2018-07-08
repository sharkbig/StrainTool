import setuptools
import codecs
import os
import re

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("[ERROR] Unable to find version string.")

setuptools.setup(name='pystrain',
      version=find_version("pystrain", "__init__.py"),
      description='Python Strain Tensor estimation tool.',
      url='https://github.com/DSOlab/StrainTool.git',
      author='Xanthos Papanikolaou, Demitris Anastasiou',
      author_email='xanthos@mail.ntua.gr, danast@mail.ntua.gr',
      packages=setuptools.find_packages(),
      install_requires=['numpy', 'scipy']
      )
