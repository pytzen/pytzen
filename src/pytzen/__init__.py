from abc import ABCMeta
import json
import threading
import logging
import os
import sys
import glob as gb


class MetaType(ABCMeta):
    """
    A metaclass that combines the initialization of derived classes 
    and the `ProtoType` base class.
    
    Methods:
    - __new__: Create and return a new object. Also, it ensures the 
        `ProtoType` base class's `__init__` is executed for derived 
        classes.
    """

    def __new__(cls:type, 
                cls_name:str, 
                cls_bases:tuple[type], 
                cls_objects:dict) -> type:
        if cls_bases and '__init__' in cls_objects:
            derived_cls_init = cls_objects['__init__']
            def init(self, **kwargs):
                ProtoType.__init__(self, **kwargs)
                derived_cls_init(self, **kwargs)
            cls_objects['__init__'] = init
        return super().__new__(cls, cls_name, cls_bases, cls_objects)


class ProtoType(metaclass=MetaType):
    """
    A base prototype class which automates several processes such as 
    logging, JSON data storage, and dynamic documentation generation.

    Attributes:
    - log_level (str): Logging level, defaulting to 'INFO'.
    - log (LogBuild): Logging utility instance.
    - data_lock (threading.Lock): Lock for thread-safe data access. It 
        must be used when working with concurrency and self.data objects 
        in derived classes.
    - data (SharedData): Shared data instance.

    Methods:
    - close: Serializes the shared and stored data of the `ProtoType` 
        instances and writes it to a configuration JSON file. 
        `self.data` objects serializes its names and types and 
        `self.data.store` objects serializes its values.
    """

    def __init__(self, **kwargs) -> None:
        for attribute_name, value in kwargs.items():
            setattr(self, attribute_name, value)
        full_class_name:str = f'{self.__module__}.{self.__class__.__name__}'
        self.log_level: str = kwargs.get('log_level', 'INFO')
        self.log = LogBuild(name=full_class_name, level=self.log_level)
        self.data_lock = threading.Lock()
        with self.data_lock:
            if not hasattr(ProtoType, 'data'):
                ProtoType.data = SharedData()
            doc_gen = DocGen({**self.__dict__, **self.__class__.__dict__})
            if 'classes' not in ProtoType.data.config:
                ProtoType.data.config['classes'] = {}
            ProtoType.data.config['classes'][full_class_name] = doc_gen.doc

    def close(self) -> None:
        data_share = {attr_name: type(val).__name__ 
                      for attr_name, val in ProtoType.data.__dict__.items() 
                      if not callable(getattr(ProtoType.data, attr_name))}
        data_store = {attr_name: val for attr_name, val 
                      in ProtoType.data.store.__dict__.items()}
        ProtoType.data.config['shared_data'] = data_share
        ProtoType.data.config['stored_data'] = data_store
        with open(ProtoType.data.config_json_path, 'w') as json_file:
            json.dump(ProtoType.data.config, json_file, indent=4)


class LogBuild:
    """
    A custom logging utility that provides a convenient interface 
    for setting up and using loggers.

    Attributes:
    - logger (logging.Logger): Logger instance with custom 
        configurations.

    Methods:
    - debug: Logs a debug level message.
    - info: Logs an info level message.
    - warning: Logs a warning level message.
    - error: Logs an error level message.
    - critical: Logs a critical level message.
    """    

    def __init__(self, name:str, level:str) -> None:
        self.logger: logging.Logger = logging.getLogger(name)
        self.logger.propagate = False
        level_mapping = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }
        set_level = level_mapping.get(level, logging.INFO)
        self.logger.setLevel(set_level)
        if not self.logger.handlers:
            msg = '%(levelname)s|%(asctime)s|%(message)s|%(name)s'
            formatter = logging.Formatter(msg)
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def debug(self, message:str) -> None:
        self.logger.debug(message)

    def info(self, message:str) -> None:
        self.logger.info(message)

    def warning(self, message:str) -> None:
        self.logger.warning(message)

    def error(self, message:str) -> None:
        self.logger.error(message)

    def critical(self, message:str) -> None:
        self.logger.critical(message)


class DocGen:
    """
    A documentation generator that introspects a given object and 
    produces a structured documentation dictionary.

    Attributes:
    - attrs (dict): Attributes of the object to be documented.
    - doc (dict): Structured documentation generated from the provided 
        attributes.

    Methods:
    - _generate_doc_dict: Generates a dictionary with detailed 
        documentation for methods and attributes.
    - _flatten_docstring: Removes newlines and unnecessary whitespace 
        from a docstring.
    """

    def __init__(self, attrs:dict) -> None:
        self.attrs = attrs
        self.doc = {
            'docstring': self._flatten_docstring(attrs.get('__doc__')),
            'attributes': {},
            'methods': {}
        }
        self._generate_doc_dict()

    def _generate_doc_dict(self) -> None:
        for attr_name, attr_value in self.attrs.items():
            if callable(attr_value) and attr_name != '__init__':
                self.doc['methods'][attr_name] = \
                    self._flatten_docstring(attr_value.__doc__)
            else:
                if not attr_name.startswith('_'):
                    self.doc['attributes'][attr_name] = \
                        type(attr_value).__name__

    def _flatten_docstring(self, docstring) -> str|None:
        if not docstring:
            return None
        return ' '.join(docstring.split())


class SharedData:
    """
    Manages shared data for the application, including the retrieval 
    and storage of configuration data from/to a JSON file.

    Attributes:
    - config_json_path (str): Path to the configuration JSON file.
    - config (dict): Parsed contents of the configuration JSON file.
    - store (StoredData): A dynamically created object to store data. 
        Objects assigned to self.data.store will raise error if not JSON 
        serializable.

    Methods:
    - _get_default_json: Determines the default JSON configuration file 
        based on the current directory contents.
    - _get_json: Reads and returns the contents of a given JSON file.
    - _get_args: Parses command line arguments and returns them as a 
        dictionary.
    - _get_env: Retrieves environment variables that correspond to the 
        provided configuration keys.
    - _generate_config: Generates a final configuration dictionary based 
        on the values found in the JSON file, command line arguments, 
        and environment variables.
    """

    def __init__(self) -> None:
        self.config_json_path:str = (os.environ.get('CONFIG_JSON_PATH') or
                                     self._get_default_json())
        self.config:dict = self._generate_config()
        StoredData = type('StoredData', (object,), {})
        setattr(self, 'store', StoredData())

    def _get_default_json(self) -> str:
        json_files = gb.glob('./*.json')
        info = "Please, specify the desired file using the "\
            "CONFIG_JSON_PATH environment variable, or let a single JSON "\
            "in the current directory."
        if len(json_files) == 1:
            return json_files[0]
        elif len(json_files) > 1:
            val_err = "Multiple JSON files found in the current directory."
            raise ValueError(f'{val_err} {info}')
        else:
            file_err = "No JSON file found in the current directory."
            raise FileNotFoundError(f'{file_err} {info}')

    def _get_json(self, json_path) -> dict:
        with open(json_path, 'r') as file:
            return json.load(file)

    def _get_args(self) -> dict:
        arg_dict = {}
        for arg in sys.argv[1:]:
            if arg.startswith('--'):
                key, value = arg[2:].split('=')
                arg_dict[key] = value
        return arg_dict

    def _get_env(self, config_dict) -> dict:
        env_dict = {}
        for key in config_dict.keys():
            if os.environ.get(key.upper()):
                env_dict[key] = os.environ.get(key.upper())
        return env_dict

    def _generate_config(self) -> dict:
        config:dict = self._get_json(self.config_json_path)
        arg_dict = self._get_args()
        env_dict = self._get_env(config)
        output_config = {}
        for var_name, default_value in config.items():
            env_val = env_dict.get(var_name, default_value)
            final_val = arg_dict.get(var_name, env_val)
            output_config[var_name] = final_val
        return output_config