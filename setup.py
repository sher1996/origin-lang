from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="origin-lang",
    version="0.1.0",
    author="Origin Language Team",
    description="A visual programming language with live execution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        "requests>=2.32.0",
        "pyinstaller>=5.0",
        "pip-licenses>=4.0.0",
    ],
    extras_require={
        "net": [
            "requests>=2.32.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "origin=src.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 