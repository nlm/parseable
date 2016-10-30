from setuptools import setup,find_packages

setup(
    name = "parseable",
    version = "1.0b1",
    packages = find_packages(),
    author = "Nicolas Limage",
    author_email = 'github@xephon.org',
    description = "map datastructures to objects with data validation",
    license = "MIT",
    keywords = "datastructure parsing validation",
    url = "https://github.com/nlm/parseable",
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires = [
        'schema',
    ],
    test_suite = 'test_parseable',
)
