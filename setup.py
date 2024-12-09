from setuptools import setup, find_packages

# Read the content of your README file
with open("README_PyPi.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='aimon',
    python_requires='>3.8.0',
    packages=find_packages(),
    version="0.8.1",
    install_requires=[
        "annotated-types==0.6.0",
        "anyio==4.4.0",
        "certifi==2023.7.22",
        "distro==1.8.0",
        "exceptiongroup==1.2.2",
        "h11==0.14.0",
        "httpcore==1.0.2",
        "httpx==0.25.2",
        "idna==3.4",
        "pydantic==2.9.2",
        "pydantic-core==2.23.4",
        "sniffio==1.3.0",
        "typing-extensions==4.12.2"
    ],
    author='AIMon',
    author_email='info@aimon.ai',
    description='The AIMon SDK that is used to interact with the AIMon API and the product.',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
