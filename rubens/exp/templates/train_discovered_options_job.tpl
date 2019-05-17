{% extends "base.tpl" %}
{% block variables %}
config_path = {{ config_path }}
options_path = {{ args }}
{% endblock %}
{% block arguments %}
Arguments = -m psr.train -c $(config_path) --options $(options_path)
{% endblock %}

