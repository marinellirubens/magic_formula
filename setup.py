from setuptools import setup, find_packages

setup(
    name='magic_formula',
    version='1.0.4',
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "magic_formula = magic_formula.main:main",
        ]
    },
    url='https://github.com/marinellirubens/magic_formula',
    author='Rubens Marinelli Ferreira',
    author_email='marinelli.rubens@gmail.com',
    description="Program to implement joel greenblat's magic formula",
    install_requires=[
        'pandas>=1.1.4',
        'openpyxl>=2.0.7',
        'yahooquery',
        'bs4',
        'requests>=2.25.1',
        'numpy>=1.1.2',
        'sqlalchemy',
    ]
)
