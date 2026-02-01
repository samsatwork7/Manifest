from setuptools import setup, find_packages

setup(
    name="manifest-recon",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "aiohttp",
        "dnspython",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "manifest=manifest.main:main"
        ]
    },
    author="Your Name",
    description="Manifest v1.0 — A Modern Reconnaissance Framework",
    url="https://github.com/yourusername/manifest",
    license="MIT",
)
