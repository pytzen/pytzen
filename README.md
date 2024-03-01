> PYTZEN is designed for developers and data scientists to sketch out data pipelines and delve into metaprogramming. Primarily designed for the Proof of Concept (POC) and Minimum Viable Product (MVP) stages, the package stands out for facilitating inheritance-driven development of data processing workflows and offers a practical scenario for exploring metaprogramming. This experimental tool aims for educational purposes, encouraging users to learn through experimentation and application. Whether for prototyping or learning advanced Python features, the code offers structured yet flexible experimentation for both innovation and education.

## Features

### Namespaces
The pipeline is isolated as a microservice application's code, with its own `module` functionality. By creating a namespace, you are cloning the package, not just creating an alias. `pytzen` is the original namespace from which your new isolated source will come from. It is the source pattern used for configuration.
```python
import pytzen
pytzen.DIR = 'path/to/your/docs/folder'
extract = pytzen.new_namespace('extract')
transform = pytzen.new_namespace('transform')
load = pytzen.new_namespace('load')
```

### `@dataclass` syntax and class documentation
PYTZEN metaprogramming benefits from the `__init__` suppression in the `@dataclass` decorator, among other features. Its usage is mandatory by the `pytzen.MetaType` metaclass.
```python
from dataclasses import dataclass
@dataclass
class DataClassFeatures:
    attribute: str = 'Milk and honey attributes.'
    number: int = 137
```

### Attributes available in all namespaces from a single `config.JSON` file
The `config.json` file must be placed in the `pytzen.DIR` folder. Its contents are available for the entire `pytzen` based application.
```python
@dataclass
class AttributesFromConfig(extract.ProtoType):
    def get_config(self):
        print(self.config.milky_attribute)
```

### Attributes value optionally stored in JSON
The JSON file for storage will be placed in the `pytzen.DIR` folder, prefixed with the namespace. For the `extract` service it will be `extract_store.json`.
```python
@dataclass
class AttributesKeeper(extract.ProtoType):
    def save_it(self):
        milk_for_tomorrow = 'White and cold.'
        sweet_bottles = {'honey': 7, 'milk': 11}
        self.store('milk', milk_for_tomorrow)
        self.store('bottles', sweet_bottles)
```

### Logger events optionally stored in JSON (whether printed or not)
The log function includes a timestamp before the message. It will be saved the same way as the store: `extract_log.json`.
```python
@dataclass
class LogKeeper(extract.ProtoType):
    def log_it(self):
        hot_milk = 'The milk boiled.'
        self.log(hot_milk, stdout=False)
```

### Documentation for each class is stored in JSON
When the namespace is closed, a classes documentation file is saved: `extract_dataclasses.json`.
```python
extract.MetaType.close()
```
### Attributes are immutable and must have a unique name by namespace
Once the attribute is declared, it must be accessed by the `data` type container. Its value cannot be changed, neither its name declared in another class in the same namespace.
```python
@dataclass
class AttributesUsage(extract.ProtoType):
    n: int = 1

    def get_number(self):
        print(self.data.n)
```

## Google Colab Docs
- [Metaprogramming Study](https://study.pytzen.com/)
- [Package Usage](https://usage.pytzen.com/)

## Source Code
```python
import json
import sys
import importlib.util
import os
from datetime import datetime
from dataclasses import dataclass, field



DIR = os.getcwd()


def new_namespace(namespace: str):
    """
    Creates and returns a new namespace as a module, isolated from the 
    original pytzen package.

    This function dynamically imports the pytzen package, then creates a 
    new module object based on the pytzen specification. It sets the 
    newly created module's MetaType.NAMESPACE attribute to the provided 
    namespace string. The new namespace is also added to the 
    sys.modules dictionary, making it recognized as a legitimate 
    module.

    Args:
    namespace: The name of the new namespace to create. This name is 
        used to isolate the created module and its configurations from 
        other modules or namespaces.

    Returns:
    module: A new module object that represents the isolated namespace. 
        This module is a clone of the pytzen package, but with its 
        MetaType.NAMESPACE attribute set to the given namespace name, 
        allowing for isolated configuration and operation within this 
        new context.
    """

    pytzen = importlib.util.find_spec('pytzen')
    vars()[namespace] = importlib.util.module_from_spec(pytzen)
    pytzen.loader.exec_module(vars()[namespace])
    sys.modules[namespace] = vars()[namespace]
    vars()[namespace].MetaType.NAMESPACE = namespace

    return vars()[namespace]



class MetaType(type):
    """Metaclass for ProtoType class. It is responsible for adding the 
    meta_attr attribute to the class and initializing the ProtoType 
    class.

    Attributes:
    NAMESPACE: Class attribute set to the given namespace name.
    
    Methods:
        __new__: Adds the meta_attr attribute to the class.
        __call__: Initializes the ProtoType class.
        log: Adds a message to the log attribute.
        store: Adds a value to the store attribute.
        close: Closes the namespace and stores the data.
    """

    NAMESPACE: str = None
    def __new__(cls, name, bases, attrs) -> type:
        """Adds log, store and close methods to the class.
        
        Args:
            name: Class name.
            bases: Class bases.
            attrs: Class attributes.
        
        Returns:
            new_cls: Class with the new methods.
        """

        attrs['log'] = cls.log
        attrs['store'] = cls.store
        attrs['close'] = cls.close
        new_cls = super().__new__(cls, name, bases, attrs)

        return new_cls
    

    def __call__(self, *args, **kwargs) -> object:
        """Initializes the ProtoType class. It is called when the 
        derived class is instantiated.
        
        Args:
            *args: Arguments.
            **kwargs: Keyword arguments.
        
        Returns:
            object: Instance of the derived class.
        """
        
        ProtoType.__init__(self)

        return super().__call__(*args, **kwargs)
    

    @classmethod
    def log(cls, message, stdout=True, write=True) -> None:
        """Adds a message to the log attribute. The message is stored 
        with the current timestamp.
        
        Args:
            message: Message to be stored.
            stdout: If True, the message is printed.
            write: If True, the message is stored.

        Returns:
            None
        """

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        if write:
            ProtoType.data.log[timestamp] = message
        if stdout:
            print(f'{timestamp}: {message}')


    @classmethod
    def store(cls, name, value) -> None:
        """Adds a value to the store attribute.
        
        Args:
            name: Name of the value.
            value: Value to be stored.
        
        Returns:
            None
        """

        ProtoType.data.store[name] = value
    

    @classmethod
    def close(cls) -> None:
        """Closes the classes and stores the pipeline information. It 
        must be called after the last derived class is used.
        
        Returns:
            None
        """

        namespace = MetaType.NAMESPACE
        pack = {
            f'{namespace}_dataclasses.json': ProtoType.data.classes,
            f'{namespace}_log.json': ProtoType.data.log,
            f'{namespace}_store.json': ProtoType.data.store,
        }
        for k, v in pack.items():
            if v:
                path = os.path.join(sys.modules['pytzen'].DIR, k)
                with open(path, 'w') as json_file:
                    json.dump(v, json_file, indent=4)



class ProtoType(metaclass=MetaType):
    """Base class for all derived classes. It is responsible for storing 
    the pipeline information.

    Class Attributes:
        DIR: Output path where the config.json must be located.
    
    Attributes:
        class_path: Path of the class.
        config: Configuration file.
        data: Pipeline information.
    
    Methods:
        __init__: Initializes the class.
        __setattr__: Adds an attribute to the class.
    """

    def __init__(self) -> None:
        """Initializes the class. It is called when the derived class 
        is instantiated by the controled behavior of 'MetaType'. 
        
        Returns:
            None
        """
        self.class_path = f'{self.__module__}.{self.__name__}'

        if not hasattr(ProtoType, 'config'):
            path = os.path.join(sys.modules['pytzen'].DIR, 'config.json')
            with open(path, 'r') as json_file:
                config = json.load(json_file)
            ProtoType.config = type('ConfigurationFile', (), config)

        if not hasattr(ProtoType, 'data'):
            ProtoType.data = SharedData()
        ProtoType.data.classes[self.class_path] = {
            'attributes': {},
            'methods': [k for k, v in self.__dict__.items() 
                        if callable(v) and '__' not in k],
        }
    

    def __setattr__(self, key, value) -> None:
        """Adds an attribute to the class. It is called when an 
        attribute is added to the derived class.
        
        Args:
            key: Attribute name.
            value: Attribute value.
            
        Returns:
            None
        """

        setattr(ProtoType.data, key, value)
        attr_type = str(type(value).__name__)
        ProtoType.data.classes[self.class_path]\
            ['attributes'][key] = attr_type



@dataclass
class SharedData:
    """Dataclass for storing the pipeline information.
    
    Attributes:
        classes: Classes used in the pipeline.
        log: Log messages.
        store: Stored values.
    """
    classes: dict = field(default_factory=dict)
    log: dict = field(default_factory=dict)
    store: dict = field(default_factory=dict)
    

    def __setattr__(self, key, value) -> None:

        if hasattr(self, key):
            error = f"Attribute '{key}' already exists and cannot be changed."
            raise AttributeError(error)
        else:
            super().__setattr__(key, value)
```