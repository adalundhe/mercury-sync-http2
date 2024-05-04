from typing import Dict, Iterator, List, Literal, Optional, Tuple, Union
from urllib.parse import ParseResult, urlencode, urlparse

import orjson
from pydantic import BaseModel, StrictBytes, StrictInt, StrictStr

from .types import HTTPCookie, HTTPEncodableValue

NEW_LINE = '\r\n'

class HTTP2Request(BaseModel):
    url: StrictStr
    parsed: ParseResult
    method: Literal[
        "GET", 
        "POST",
        "HEAD",
        "OPTIONS", 
        "PUT", 
        "PATCH", 
        "DELETE"
    ]
    cookies: Optional[List[HTTPCookie]]=None
    auth: Optional[Tuple[str, str]]=None
    params: Optional[Dict[str, HTTPEncodableValue]]=None
    headers: Dict[str, str]={}
    data: Union[
        Optional[StrictStr],
        Optional[StrictBytes],
        Optional[BaseModel]
    ]=None
    redirects: StrictInt=3

    class Config:
        arbitrary_types_allowed=True

    def parse_url(self):
        return urlparse(self.url)

    @property
    def size(self):
        if self.encoded_data:
            return len(self.encoded_data)

        else:
            return 0

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.encoded_data = None

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value: Dict[str, str]):
        self._headers = value
        self._header_items = list(value.items())
        self.encoded_headers = None

    def encode_data(self):

        encoded_data: Optional[bytes] = None
        if self._data:
            if isinstance(self._data, Iterator):
                chunks = []
                for chunk in self._data:
                    chunk_size = hex(len(chunk)).replace("0x", "") + NEW_LINE
                    encoded_chunk = chunk_size.encode() + chunk + NEW_LINE.encode()
                    self.size += len(encoded_chunk)
                    chunks.append(encoded_chunk)

                self.is_stream = True
                encoded_data = chunks

            else:

                if isinstance(self._data, dict):
                    encoded_data = orjson.dumps(
                        self._data
                    )

                elif isinstance(self._data, tuple):
                    encoded_data = urlencode(
                        self._data
                    ).encode()

                elif isinstance(self._data, str):
                    encoded_data = self._data.encode()

        self.encoded_data = encoded_data

        return encoded_data

    def encode_headers(self) -> List[Tuple[bytes, bytes]]:
    
        encoded_headers = [
            (b":method", self.method),
            (b":authority", self.parsed.hostname),
            (b":scheme", self.parsed.scheme),
            (b":path", self.parsed.path),
        ]

        encoded_headers.extend([
            (
                k.lower(), 
                v
            )
            for k, v in self._headers.items()
            if k.lower()
            not in (
                b"host",
                b"transfer-encoding",
            )
        ])
        
        return encoded_headers