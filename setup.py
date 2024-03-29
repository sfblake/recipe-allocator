from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as f:
    requirements_lines = f.readlines()
install_requires = [r.strip() for r in requirements_lines]

setup(
    name="recipe-allocator",
    version="0.1",
    author="Samuel Blake",
    author_email="samuelfblake@gmail.com",
    description="Order allocation algorithm",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/sfblake/recipe-allocator",
    packages=find_packages(),
    install_requires=install_requires,
    test_suite='nose.collector',
    tests_require=['nose>=1.3.7'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)