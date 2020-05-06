from setuptools import setup


setup(
    name='chnroutes2020',
    python_requires='>=3',
    version='0.0.1',
    description='Script to generate China-specific IPv4 rules',
    url='https://github.com/mckelvin/chnroutes2020',
    author='mckelvin',
    author_email=' mckelvin@users.noreply.github.com',
    packages=['chnroutes2020'],
    install_requires=[
        "click",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "chnroutes2020 = chnroutes2020.__main__:cli",
        ]
    }
)
