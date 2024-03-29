from setuptools import setup, find_namespace_packages

setup(
    name='vsdkx-addon-tracking',
    url='https://github.com/natix-io/vsdkx-addon-tracking.git',
    author='Helmut',
    author_email='helmut@natix.io',
    namespace_packages=['vsdkx', 'vsdkx.addon'],
    packages=find_namespace_packages(include=['vsdkx*']),
    dependency_links=[
        'git+https://github.com/natix-io/vsdkx-core#egg=vsdkx-core'
    ],
    install_requires=[
        'vsdkx-core',
        'numpy>=1.18.5',
        'scipy>=1.4.1'
    ],
    version='1.0',
)
