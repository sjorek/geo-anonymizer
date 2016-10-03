# geo-anonymizer

[![PyPi](https://img.shields.io/pypi/v/geoanonymizer.svg)](https://pypi.python.org/pypi/geoanonymizer)

Consistent interface for anonymizing streams of geocoordinates.

## Features

- …

## Getting Started

### Installation

To get started:

```
$ pip install geoanonymizer
```

### Example

Open tabular stream from csv source:

```python
from tabulator import Stream
from geoanonymizer import geoanonymize_tabulator_stream as geoanonymize

with Stream('path.csv', headers=1, post_parse=geoanonymize) as stream:
    print(stream.headers) # will print headers from 1 row
    for row in stream:
        print(row)  # will print row values list
```

## Documentation

### …

…

### exceptions

The library provides various of exceptions. Please consult with docstrings.

## Read more

- [Docstrings](https://github.com/sjorek/geoanonymizer/tree/master/geoanonymizer)
- [Changelog](https://github.com/sjorek/geoanonymizer/commits/master)
- [Contribute](CONTRIBUTING.md)

Enjoy!
