import pytest
from evalgov.portfolio import PortfolioTarget


@pytest.mark.parametrize('url', ['http://remote.example', 'https://host/ask', 'https://host/?key=secret'])
def test_portfolio_target_restricts_origin(url):
    with pytest.raises(ValueError):
        PortfolioTarget('rag', url, 'test-only')


def test_usage_is_zero_when_local_extractive():
    assert PortfolioTarget.answer('text', ['policy'], False, [])['usage'] == {'input_tokens': 0, 'output_tokens': 0}
