from setuptools import setup
import os


with open("README.md", "r") as fh:
    long_description = fh.read()

# if people don't have git
# def get_git_revision_short_hash():
#     """determines the git revision; only works if the packages was checked
#     out using git"""
#     ghash = subprocess.check_output(
#         ['git', 'describe', '--always'], cwd=os.getcwd())
#     try:
#         # ghash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
#         ghash = subprocess.check_output(
#             ['git', 'describe', '--always'], cwd=os.getcwd())

#         ghash = ghash.decode('utf-8').rstrip()
#     except:
#         # git isn't installed
#         ghash = 'no.checksum.error'
#     return '%s' % ghash

def version():
    """ Get version from __init__.py."""
    v = None
    with open(os.path.join('./meshRW', '__init__.py')) as f:
        for line in f:
            if line.startswith('__version__'):
                v = line.replace("'", '').split()[-1]
                break
        return v



this_version = version()
print('version:', this_version)


setup(
    name="meshRW",
    version=this_version,
    author="L. Laurent",
    author_email="luc.laurant@lecnam.net",
    description="A tool to read and write MSH (v2) and VTK files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luclaurent/meshRW",
    zip_safe=False,
    packages=['meshRW'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy'
    #     'wand>=0.5.9',
    #     'lxml>=3.5.0',
    #     'pyparsing>=2.4.6',
    #     'wheel>=0.29.0',
    #     'markdown'
    ],
    python_requires='>=3.5'
)