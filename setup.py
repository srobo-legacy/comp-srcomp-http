from setuptools import setup, find_packages

with open('README.md') as f:
    description = f.read()

setup(name = "sr.comp.http",
      version = "1.0",
      packages = find_packages(),
      namespace_packages = ['sr', 'sr.comp'],
      package_data = {'sr.comp.http': ['logging-*.ini']},
      description = description,
      author = "Peter Law",
      author_email = "PeterJCLaw@gmail.com",
      install_requires = ['nose >=1.3, <2',
                          'PyYAML >=3.11, <4',
                          'sr.comp >=1.0, <2',
                          'mock >=1.0.1, <2',
                          'six >=1.8, <2',
                          'Flask >=0.10, <0.11',
                          'simplejson >=3.6, <4',
                          'python-dateutil >=2.2, <3']
      )

