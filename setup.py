import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qswift",
    version="0.0.11",
    author="kouhei nakaji",
    author_email="nakajijiji@gmail.com",
    description="You can receive the message 'Hello!!!'",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/konakaji/qswift",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "qwrapper @ git+ssh://git@github.com/konakaji/qwrapper.git",
        "benchmark @ git+ssh://git@github.com/konakaji/benchmark.git",
        "bitarray>=2.6.1"
    ],
    python_requires='>=3.6',
)
