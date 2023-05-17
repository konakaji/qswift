import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qswiftencoder",
    version="0.0.5",
    author="kouhei nakaji",
    author_email="nakajijiji@gmail.com",
    description="You can receive the message 'Hello!!!'",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/konakaji/qswiftencoder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "qwrapper @ git+ssh://git@github.com/konakaji/qwrapper.git"
        "benchmark @ git+ssh://git@github.com/konakaji/benchmark.git"
    ],
    python_requires='>=3.6',
)
