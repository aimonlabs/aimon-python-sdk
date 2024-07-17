from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("CHANGELOG.md", "r", encoding="utf-8") as fh:
    changelog = fh.read()

setup(
    name='aimon',
    python_requires='>3.8.0',
    packages=find_packages(),
    version="0.4.0",
    install_requires=[
        "httpx",
        "distro",
        "pydantic==2.7.1",
        "pydantic-core==2.18.2",
    ],
    author='AIMon',
    author_email='info@aimon.ai',
    description='The AIMon SDK that is used to interact with the AIMon API and the product.',
    long_description=long_description + "\n\n" + changelog,
    long_description_content_type='text/markdown',
)
