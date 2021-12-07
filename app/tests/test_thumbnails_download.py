from unittest.mock import patch

import pytest

from main import app


@pytest.mark.asyncio
def test_regex_matching(client):
    url = app.url_path_for("create_item")
    test_item = {
        "url"  : "https://www.some.domain.com/product/1",
        "price": 1.0,
        "tags" : ['tag_1']
    }
    with patch("api.api_v1.endpoints.items.download_thumbnail") as mocked_download_thumbnail:
        client.post(url, json=test_item)
        mocked_download_thumbnail.assert_called_once_with("https://some.domain.com/favicon.ico",1)