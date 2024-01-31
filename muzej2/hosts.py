from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'zbirka', 'inventura.urls', name='zbirka'),
    host(r'www', 'inventura.urls', name='www'),
    host(r'revije', 'inventura.revije-urls', name='revije'),
    host(r'evidenca', 'evidenca.urls', name='evidenca'),
    host(r'api', 'inventura.api-urls', name='api'),
)