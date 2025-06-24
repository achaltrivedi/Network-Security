# This setup file is essential part for packaging and distributing the project. It is used by setuptools
# to define the package metadata, dependencies, and other configurations.

from setuptools import setup, find_packages
from typing import List

def get_requirements() -> List[str]:         #this function returns a list of requirements

    requirement_lst:List[str] = []  # Initialize an empty list to store requirements    
    try:
        with open('requirements.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                requirement=line.strip()
                ##ignore empty lines and -e.
                if requirement and requirement != '-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirements.txt file not found. Please ensure it exists in the project directory.")
        
    return requirement_lst

print(get_requirements())  # Print the list of requirements for debugging purposes

setup(
    name='network_security',
    version='0.0.1',
    author='Achal Trivedi',
    author_email='achal.trivedi1325@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements()
)