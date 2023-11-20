<link rel="stylesheet" href="https://pablo.haus/styles.css">

`pytzen` provides a minimal structured approach to data science pipelines, encompassing modularity, automation, and documentation in one package.

![pytzen.github.io](https://pablo.haus/concepts/pytzen-github-io.png)

## Inspiration
Inspired by Ikigai, Kaizen, Pomodoro Technique, Hara Hachi Bu, Shoshin, Wabi-sabi.

### Minimalistic Principles
**Simplicity**: This is the core of minimalism. Whether it's design, writing, or lifestyle, the focus is on simplicity. It's about removing the unnecessary and focusing on what truly matters.

**Clarity**: Everything in minimalism should be easily understood. In design, this often means using straightforward graphics and concise text.

**Functionality**: Every element should have a purpose. If it doesn't add value or function, it's often removed in a minimalist approach.

**Limitation**: This could mean limiting colors in a design, words in writing, or possessions in a minimalist lifestyle.

**Harmony**: Even though there might be fewer elements, they should work harmoniously together.

**Intentionality**: Every choice made should be deliberate. Minimalism isn't about deprivation, but rather making intentional decisions.

### Python Minimalistic Code
- Objects names and type hints are documentation.
- Docstrings for classes and methods in all-in-one paragraph.
- Reduce classes and methods to its minimal functionality.

## Usage & Limitations Overview

### Disclaimer
This library is offered 'as-is' with **no official support, maintenance, or warranty**. Primarily, `pytzen` is an experimentation, which may not be apt for production settings. Users are encouraged to delve into the library but should note that the developers won't actively address arising issues.

### Usage Caution
`pytzen` is primarily intended for prototyping, such as in Proof-of-Concept (POC) or Minimum Viable Product (MVP) stages. We are not liable for issues arising from the library's usage in production environments. Before considering any wider implementation, users should extensively test and vet the library in a safe, controlled environment.

## Documentation
In essence, the code provides a framework for creating classes with a standard logging mechanism, a way to generate documentation for them, and a shared configuration and data attributes manager.

### Minimalistic Approach in `pytzen` Package
1. **`pytzen.MetaType`**: 
   This is a metaclass that inherits from `ABCMeta`. When a new class is created using this metaclass, it modifies the `__init__` method of the class to ensure that both the `__init__` of the `ProtoType` class and the derived class's `__init__` (if it exists) are called. This allows classes that inherit from `ProtoType` to have custom initialization methods while also ensuring that the base class's initialization method is invoked.
2. **`pytzen.ProtoType`**: 
   This class serves as a prototype for other classes, and it uses the `MetaType` metaclass. During its initialization, it sets up attributes based on keyword arguments, creates a logging instance, establishes a threading lock for data safety, and initializes shared data for the class. It also has a method called `close` that writes configuration data to a JSON file.
3. **`pytzen.LogBuild`**: 
   This class is a simple wrapper around Python's built-in logging module. When an instance is created, it sets up a logger with a given name and level. It has methods for each log level (debug, info, warning, error, critical) which allow it to log messages of those levels.
4. **`pytzen.DocGen`**: 
   This class takes in a dictionary of attributes and provides functionality to generate a documentation dictionary for them. The dictionary includes the class's docstring, its methods and their respective docstrings, and its non-callable attributes with their types. This is a utility class meant to aid in creating documentation for classes on-the-fly.
5. **`pytzen.SharedData`**: 
   This class manages configuration data for the application. It can read configurations from a JSON file, command-line arguments, and environment variables. When initialized, it combines these sources of configurations, giving priority to command-line arguments over environment variables and then default values from the JSON. It's essentially a configuration manager for the application.

### Installation
`pip install pytzen`

