from setuptools import setup

with open("README.md") as f:
    readme = f.read()

with open("rst2pyi/__init__.py") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split('"')[1]

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f]

setup(
    name="rst2pyi",
    description="convert reStructuredText annotations to PEP 484 type stubs",
    long_description=readme,
    long_description_content_type="text/markdown",
    version=version,
    author="John Reese",
    author_email="john@noswap.com",
    url="https://github.com/jreese/rst2pyi",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
    ],
    license="MIT",
    packages=["rst2pyi", "rst2pyi.tests"],
    setup_requires=["setuptools>=38.6.0"],
    install_requires=requirements,
    tests_require=[],
    test_suite="rst2pyi.tests",
    entry_points={"console_scripts": ["rst2pyi = rst2pyi.main:main"]},
)
