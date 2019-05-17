# Condor variables can be overwritten at run-time using 'var = value'
# e.g. condor_submit <( submit.py ) 'N = 5'
# Overwriting actually just pre-pends.. so not so much overwriting as supplying

# If I set this it wouldn't be overwritable
# N = 1
{% block variables %}
# Variable declarations go here
args =
{% endblock %}

Executable  = {{ python }}
Universe = vanilla
{% block arguments %}
Arguments = $(args)
{% endblock %}

{% if prefix and prefix != '' %}
JobBatchName = '{{ prefix }}'
# Can't find anywhere what the + was for
# +Prefix = '{{ prefix }}';
{% endif %}

# Preference set to CPU
Rank = KFlops
Request_cpus = 1
Requirements = ((Arch == "INTEL" && OpSys == "LINUX") || \
               (Arch == "X86_64" && OpSys =="LINUX"))
request_memory = 4000

Error = condor_logs/{{ prefix }}$(cluster).err
Output = condor_logs/{{ prefix }}$(cluster).out
Log = condor_logs/{{ prefix }}$(cluster).log

Initialdir = {{ base_path }}

Next_job_start_delay = 1
Max_retries = 3
# Restart the job when exit code wasn't 0 and it wasn't killed
On_exit_remove = (ExitBySignal == False) && (ExitCode == 0)

# I think this wasn't working or something so had to manually supply it as env_string
Getenv = True
Environment = "{{env_string}}"

Queue $(N)

