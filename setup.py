from setuptools import setup, find_packages

setup(
    name='aimon',
    python_requires='>3.8.0',
    packages=find_packages(),
    version="0.3.1",
    install_requires=[
        "requests"
    ],
    author='AIMon',
    author_email='info@aimon.ai',
    description='The AIMon SDK that is used to interact with the AIMon API and the product.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
