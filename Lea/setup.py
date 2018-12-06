from setuptools import setup, find_packages

setup(
    name='lea_codes',
    version='0.1',
    description='Misc utilities',
#      url='needs a URL',
    author='Lea Dupuy',
    author_email='leadpy.gmail.com',
    license='GNU',
    packages=find_packages(),
    install_requires=['pandas'],
    zip_safe=True,
)
