from setuptools import setup, find_packages

setup(
    name="fair-division",
    version="1.0.0",
    description="Game-theoretic fair division algorithms with diagnostics",
    author="Research Team",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.11",
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "ortools>=9.8.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ]
    },
)
