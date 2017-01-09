from setuptools import setup, find_packages

install_requires = """
    flask
    pyyaml
""".split()

setup(
    name="bitsbox",
    packages=find_packages(),

    install_requires=install_requires,
)
