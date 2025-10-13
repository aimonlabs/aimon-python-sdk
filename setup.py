from setuptools import setup, find_packages

# Read the content of your README file
with open("README_PyPi.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='aimon',
    python_requires='>3.8.0',
    packages=find_packages(),
    version="0.12.1",
    install_requires=[
        "annotated-types~=0.6.0",
        "anyio~=4.9.0",
        "certifi~=2025.4.26",
        "distro~=1.9.0",
        "exceptiongroup~=1.2.2",
        "h11~=0.16.0",
        "httpcore~=1.0.9",
        "httpx>=0.27.2,<1.0.0",
        "idna~=3.10",
        "pydantic~=2.11.3",
        "pydantic-core~=2.33.1",
        "sniffio~=1.3.1",
        "typing-extensions~=4.13.2"
    ],
    author='AIMon',
    author_email='info@aimon.ai',
    description='The AIMon SDK that is used to interact with the AIMon API and the product.',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
