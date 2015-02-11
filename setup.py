from setuptools import setup, find_packages


with open('README.rst') as f:
    long_description = f.read()


setup(name='sr.comp.http',
      version='1.0.0',
      packages=find_packages(),
      namespace_packages=['sr', 'sr.comp'],
      package_data={'sr.comp.http': ['logging-*.ini']},
      long_description=long_description,
      author="Student Robotics Competition Software SIG",
      author_email="srobo-devel@googlegroups.com",
      install_requires=['PyYAML >=3.11, <4',
                        'sr.comp >=1.0, <2',
                        'mock >=1.0.1, <2',
                        'six >=1.8, <2',
                        'Flask >=0.10, <0.11',
                        'simplejson >=3.6, <4',
                        'python-dateutil >=2.2, <3'],
      setup_requires=['nose >=1.3, <2',
                      'Sphinx >=1.2, <2'],
      tests_require=['freezegun >=0.2.8, <0.3'],
      test_suite='nose.collector')
