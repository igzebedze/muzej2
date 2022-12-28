from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'zbirka', 'inventura.urls', name='zbirka'),
    host(r'evidenca', 'evidenca.urls', name='evidenca'),
)