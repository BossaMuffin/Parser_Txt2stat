from dataclasses import dataclass
import json

@dataclass
class Config:
    HTTP_SOURCE: str
    OUT_DIRECTORY: str
    OUT_DEFAULT_FILE_NAME: str
    OUT_DEFAULT_FILE_EXTENSION: str
    RELATIVE_OUT_PATH: str


def read(config_file: str) -> Config:
    with open(config_file, 'r') as file_in:
        data = json.load(file_in)
        return Config(**data)
