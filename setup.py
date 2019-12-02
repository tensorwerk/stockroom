import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stockroom",
    version="0.0.1",
    author="hhsecond",
    author_email="sherin@tensorwerk.com",
    description="A high level data and model versioning toolkit sits on top of hangar",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hhsecond/stockroom",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['stock = stockroom.cli:main']
    },
    install_requires=['hangar']
)
