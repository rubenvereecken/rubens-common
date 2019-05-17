{% extends "base.tpl" %}
{% block variables %}
trace_paths = {{ args }}
config_path = {{ config_path }}
{% endblock %}
{% block arguments %}
Arguments = -m irl.discover -c $(config_path) $(trace_paths)
{% endblock %}
