{% extends "base.tpl" %}
{% block variables %}
{{ super() }}
config_path = {{ config_path }}
args = -m psr.train -c $(config_path) {{ args }}
{% endblock %}
