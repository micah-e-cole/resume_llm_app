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
- {{ job.description }}
{% endfor %}

## Education
{% for edu in education %}
- {{ edu.degree }} from {{ edu.institution }} ({{ edu.years }})
{% endfor %}