from setuptools import setup, find_packages

setup(
    name="GPTViz",
    version="0.9",
    packages=find_packages(),
    include_package_data=True,

    install_requires=[
        "matplotlib",
        "numpy",
        "pyarrow", 
        "PyQt6", 
        "pyqt6_sip", 
        "setuptools", 
        "torch"
    ],

    entry_points={
        'console_scripts': [
            'GPTViz=gptviz.main:main',
        ],
    },
)