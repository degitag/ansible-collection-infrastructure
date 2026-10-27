"""Normalize proxy credentials once, independently of the consuming file format."""
import re
from urllib.parse import quote, urlsplit, urlunsplit
from ansible.errors import AnsibleFilterError


def proxy_url(value):
    if not isinstance(value, str) or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise AnsibleFilterError('Proxy URLs must be strings without control characters')
    if not value:
        return value
    try:
        parts = urlsplit(value)
        if parts.scheme not in ('http', 'https', 'socks5', 'socks5h') or not parts.hostname or parts.path not in ('', '/') or parts.query or parts.fragment:
            raise ValueError()
        _ = parts.port
        if re.search(r'''[\s\\"'`$;]''', parts.hostname):
            raise ValueError()
    except ValueError as error:
        raise AnsibleFilterError('Use an absolute HTTP(S) or SOCKS proxy URL without query or fragment') from error
    if '@' not in parts.netloc:
        return value
    userinfo, _, host = parts.netloc.rpartition('@')
    def encoded(text):
        # Existing %HH escapes survive repeated normalization; literal % is escaped.
        return re.sub(r'%(?![0-9a-fA-F]{2})', '%25', quote(text, safe='%'))
    username, separator, password = userinfo.partition(':')
    auth = encoded(username) + (':' + encoded(password) if separator else '')
    return urlunsplit((parts.scheme, auth + '@' + host, parts.path, '', ''))


def proxy_environment(values, fallback_all=False):
    if not isinstance(values, dict):
        raise AnsibleFilterError('Proxy environment must be a dictionary')
    result = {}
    for name in ('http_proxy', 'https_proxy', 'all_proxy', 'no_proxy'):
        value = values.get(name, values.get(name.upper(), ''))
        if not isinstance(value, str) or any(ord(c) < 32 or ord(c) == 127 for c in value):
            raise AnsibleFilterError('Proxy environment values must be strings without control characters')
        normalized = value if name == 'no_proxy' else proxy_url(value)
        result[name] = normalized
        result[name.upper()] = normalized
    if fallback_all:
        for name in ('http_proxy', 'https_proxy'):
            result[name] = result[name] or result['all_proxy']
            result[name.upper()] = result[name]
    return result


class FilterModule:
    def filters(self):
        return {'proxy_url': proxy_url, 'proxy_environment': proxy_environment}
