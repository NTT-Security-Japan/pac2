import logging
import os
from typing import Union
from flask import request, Response


def setup_logger(name: str, log_file: str, level: Union[int, str] = logging.INFO) -> logging.Logger:
    """
    ロガーを設定し、指定された名前、ログファイル、ログレベルで返します。
    """
    log_format = (
        '%(remote_addr)s - - [%(asctime)s] "%(method)s %(url)s %(protocol)s" '
        '%(status)s %(length)s "%(referer)s" "%(user_agent)s"'
    )

    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter(log_format))

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def log_after_request(response: Response, logger_name: str) -> Response:
    """
    hook after request procedure.
    """
    logger = logging.getLogger(logger_name)
    logger.info(
        '',
        extra={
            'remote_addr': request.remote_addr,
            'method': request.method,
            'url': request.full_path.rstrip('?'),
            'protocol': request.environ.get('SERVER_PROTOCOL'),
            'status': response.status_code,
            'length': response.calculate_content_length() or '-',
            'referer': request.referrer or '-',
            'user_agent': request.user_agent
        }
    )
    return response
