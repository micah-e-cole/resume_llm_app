# {{ name }}

## Summary
{{ summary }}

## Skills
{% for skill in skills %}
- {{ skill }}
{% endfor %}

## Work Experience
{% for job in work_experience %}
### {{ job.title }} at {{ job.company }} ({{ job.years }})
{% for bullet in job.description %}
- {{ bullet }}
{% endfor %}
{% endfor %}

## Earlier Work Experience
{% for exp in other_experience %}
### {{ exp.title }} at {{ exp.company }} ({{ exp.years }})
- {{ exp.description }}
{% endfor %}

## Volunteer Experience
{% for vol in volunteer_experience %}
### {{ vol.title }} at {{ vol.company }} ({{ vol.years }})
- {{ vol.description }}
{% endfor %}

## Education
{% for edu in education %}
### {{ edu.degree }} {{ edu.focus }} from {{ edu.institution }} ({{ edu.years }})
{% endfor %}

## Projects
{% for p in projects %}
### {{ p.title }} ({{ p.years }})
- {{ p.description }}
{% endfor %}