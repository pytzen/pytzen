import json
import os
from datetime import datetime
from dataclasses import dataclass, field



class MetaType(type):
    """Metaclass for ProtoType class. It is responsible for adding the 
    meta_attr attribute to the class and initializing the ProtoType 
    class.

    Class Attributes:
        DIR: Output path where the config.json must be located.
    
    Methods:
        __new__: Adds the meta_attr attribute to the class.
        __call__: Initializes the ProtoType class.
        log: Adds a message to the log attribute.
        store: Adds a value to the store attribute.
        close: Closes the class and stores the data.
    """
    DIR = None
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
        ProtoType.DIR = MetaType.DIR
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

        pack = {
            'dataclasses.json': ProtoType.data.classes,
            'log.json': ProtoType.data.log,
            'store.json': ProtoType.data.store,
        }
        for k, v in pack.items():
            path = os.path.join(MetaType.DIR, k)
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
    DIR = None
    def __init__(self) -> None:
        """Initializes the class. It is called when the derived class 
        is instantiated by the controled behavior of 'MetaType'. 
        
        Returns:
            None
        """
        self.class_path = f'{self.__module__}.{self.__name__}'

        if not hasattr(ProtoType, 'config'):
            path = os.path.join(ProtoType.DIR, 'config.json')
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