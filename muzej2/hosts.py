from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'zbirka', 'inventura.urls', name='zbirka'),
    host(r'revije', 'inventura.revije-urls', name='revije'),
    host(r'evidenca', 'evidenca.urls', name='evidenca'),
    host(r'api', 'inventura.api-urls', name='api'),
    host(r'app', 'inventura.app-urls', name='app')
)