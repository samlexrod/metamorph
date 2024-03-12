from setuptools import setup, find_packages

setup(
    name="metamorph",
    version="0.1.0",
    author="Samuel Rodriguez",
    author_email="rodsamuel@outlook.com",
    description="A package for de-identifying data, transforming it for privacy.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/samlexrod/metamorph",
    packages=find_packages(),
    install_requires=[
        "scikit-learn==0.24.2",
        "scrubadub==2.0.0"        
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
