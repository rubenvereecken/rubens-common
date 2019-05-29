{% extends "base.tpl" %}
{% block variables %}
## This will populate post_args, which includes logpath and seed
{{ super() }}
config_path = {{ config_path }}
args = -m psr.discovery -c $(config_path) {{ args }}
{% endblock %}
