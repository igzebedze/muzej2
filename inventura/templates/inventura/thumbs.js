window.thumbs_base64=
{   {% for i in pages %}
    "{{ forloop.counter }}": "{{ location }}/{{ i|stringformat:"08d" }}_tbthumb.jpg"{% if forloop.last %}{% else %},{% endif %}
    {% endfor %} 
}

if (typeof window.tlbr != 'undefined'){ if (typeof window.tlbr.base64thumbsLoaded != 'undefined'){ window.tlbr.base64thumbsLoaded(); } } 
