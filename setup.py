from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ReactoN",
    version="0.1.0",
    author="ASRHÜR Kimya ve Makina Sanayi A.Ş.",
    author_email="dogukan@asrhur.com",
    description="Advanced hydrogen generation system analysis, optimization and integration platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/asrhur/ReactoN",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "fastapi>=0.85.0",
        "uvicorn>=0.18.0",
        "pydantic>=1.10.0",
        "requests>=2.26.0",
    ],
)
