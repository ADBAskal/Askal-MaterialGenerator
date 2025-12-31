#!/usr/bin/env python3
"""
DayZ Texture Converter - Setup Script
A GUI tool for converting textures from Unreal/Blender to DayZ/Enfusion format
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "DayZ Texture Converter - Convert textures to DayZ/Enfusion format"

# Read requirements from requirements.txt
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Handle platform-specific requirements
                    if ';' in line:
                        requirements.append(line)
                    else:
                        requirements.append(line)
    return requirements

setup(
    name="dayz-texture-converter",
    version="1.0.0",
    author="DayZ Modder",
    description="GUI tool for converting textures to DayZ/Enfusion format",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "dayz-texture-converter=dayz_texture_converter.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    keywords="dayz texture converter smdi enfusion modding",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/dayz-texture-converter/issues",
        "Source": "https://github.com/yourusername/dayz-texture-converter",
    },
)