import logging
from urllib.parse import urljoin

import requests
from rest_framework import status


logger = logging.getLogger(__name__)


class BaseClient:
    BASE_URL = None
    TIMEOUT = 10  # in seconds

    @classmethod
    def _get_base_url(cls, **kwargs):
        return cls.BASE_URL

    @classmethod
    def send_request(cls, method, path, params=None, data=None, headers=None, verify=True, json=True, full=False,
                     **kwargs):
        request_kwargs = dict(
            method=method,
            url=urljoin(cls._get_base_url(**kwargs), path),
            timeout=cls.TIMEOUT,
            verify=verify,
        )
        if params:
            request_kwargs['params'] = params
        if data:
            if json:
                request_kwargs['json'] = data
            else:
                request_kwargs['data'] = data
        if headers:
            request_kwargs.update(headers=headers)

        try:
            response = requests.request(**request_kwargs)
        except (ConnectionError, requests.ReadTimeout) as e:
            logger.exception(e)
            return

        if response.status_code not in (status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_204_NO_CONTENT):
            logger.error(
                f'Invalid response.\n'
                f'URL: {response.url}\n'
                f'Data: {response.request.body}\n'
                f'Status: {response.status_code}\n'
                f'Response: {response.text}'
            )
            if full:
                return response
            return

        return response.json() if not full else response
