from setuptools import setup, find_packages

# Read the content of your README file
with open("README_PyPi.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='aimon',
    python_requires='>3.8.0',
    packages=find_packages(exclude=['aimon_llamaindex', 'aimon_llamaindex.*']),
    version="0.8.0",
    install_requires=[
        "httpx",
        "distro",
        "pydantic==2.9.2",
        "pydantic-core==2.23.4",
    ],
    ## Has to be installed as: pip install aimon[aimon-llamaindex]
    ## This will include the aimon_llamaindex package (which was excluded during the default installation)
    extras_require={
        "aimon-llamaindex":[
        "llama-index",
        ],
    },
    author='AIMon',
    author_email='info@aimon.ai',
    description='The AIMon SDK that is used to interact with the AIMon API and the product.',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
