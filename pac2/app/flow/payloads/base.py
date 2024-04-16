from typing import Any
from .method import gen_http_get_request_action, gen_http_post_request_action
from .method import gen_dropbox_download_action, gen_dropbox_upload_action
from pypowerautomate.actions import ScopeStatement
from random import randint


class BasePayload:
    @staticmethod
    def get_upload_method_generator(method):
        if method == "http":
            return gen_http_post_request_action
        elif method == "dropbox":
            return gen_dropbox_upload_action
        else:
            raise ValueError("Unknown method.")

    @staticmethod
    def get_download_method_generator(method):
        if method == "http":
            return gen_http_get_request_action
        elif method == "dropbox":
            return gen_dropbox_download_action
        else:
            raise ValueError("Unknown method.")

    @classmethod
    def get_payload_metadata(cls):
        """
        Generate Paylaod medadata for PAC2 Web UI.
        metadata format:
            [{
                "action":<payload class name:str>, 
                "args":[
                    [<arugument type:str>, <arugument name:str>],
                    [<arugument type:str>, <arugument name:str>],
                    ...
                ]
            }]
        """
        from . import INPUT_TYPE_MAP
        metadata = {}
        metadata["action"] = cls.__name__.replace("Payload", "")
        metadata["args"] = list()
        for arg_name, annotation in cls.__init__.__annotations__.items():
            if arg_name in INPUT_TYPE_MAP.keys():
                metadata["args"].append([INPUT_TYPE_MAP[arg_name], arg_name])
            elif annotation is None:
                metadata["args"].append(["text", arg_name])
            #  elif hasattr(annotation, '__origin__') and hasattr(annotation, '__args__'):
                # For complex types like List[int]
                # origin = annotation.__origin__.__name__
                # args = [arg.__name__ if arg is not Any else 'Any' for arg in annotation.__args__]
                # metadata[arg_name] = f"{origin}[{', '.join(args)}]"
            else:
                metadata["args"].append(["text", arg_name])
        return metadata

    def generate_payload(self) -> ScopeStatement:
        raise NotImplementedError(
            "Expect to be overridden by inherited classes")
