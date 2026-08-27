---
hide:
  - toc
---

# Schedule

<div class="schedule-table-container">
<table class="schedule-table" id="schedule-table">
<thead>
<tr>
  <th data-sort-method="none" id="week-header" class="sortable-week">Week <span class="sort-indicator">⇅</span></th>
  <th data-sort-method="none">Date</th>
  <th data-sort-method="none">Topic</th>
  <th data-sort-method="none">Links</th>
</tr>
</thead>
<tbody>
{% for week_data in weeks %}
  {% set days_in_order = [
    ('tuesday', week_data.tuesday, 'Tuesday'),
    ('thursday', week_data.thursday, 'Thursday'),
    ('friday', week_data.friday, 'Friday')
  ] %}
  {% set existing_days = days_in_order | selectattr('1') | list %}
  {% if existing_days %}
  {% set week_days = existing_days | selectattr('1.date') | list %}
  {% for day_key, day_data, day_name in existing_days %}
  <tr class="day-row"{% if loop.first %} id="week-{{ week_data.week }}"{% endif %}>
    {% if loop.first %}
    <td class="week-number" rowspan="{{ week_days | length }}">
      <strong>{{ week_data.week }}</strong>
    </td>
    {% endif %}
    <td class="date-cell">
      <div class="date-info">
        <strong>{{ day_data.date }}</strong>
        <small>{{ day_name }}</small>
      </div>
    </td>
    <td class="topic-cell">
      <div class="session-content">
        <h4 class="session-topic">
          {% if day_data.type == 'lecture' %}
          <span class="label label-green">LEC</span>
          {% elif day_data.type == 'exercise' %}
          <span class="label label-purple">EXERCISE</span>
          {% elif day_data.type == 'exam' %}
          <span class="label label-red">EXAM</span>
          {% elif day_data.type == 'holiday' %}
          <span class="label label-yellow">NO CLASS</span>
          {% endif %}
          {{ day_data.topic }}
        </h4>
        {% if day_data.due %}
        <div class="due-item">
          <span class="label label-due">SUBMIT</span> {{ day_data.due }}
        </div>
        {% endif %}
      </div>
    </td>
    <td class="links-cell">
      {% if day_data.links %}
      <div class="links-list">
        {% for link in day_data.links %}
        <div class="link-item">
          {% if link.url %}
          <a href="{{ link.url }}" class="link-item-link"{% if link.url.startswith('http') %} target="_blank" rel="noopener noreferrer"{% endif %}>{{ link.text }}</a>
          {% else %}
          <span class="link-item-name">{{ link.text }}</span>
          {% endif %}
        </div>
        {% endfor %}
      </div>
      {% endif %}
    </td>
  </tr>
  {% endfor %}
  {% endif %}
{% endfor %}
</tbody>
</table>
</div>

!!! info "How this course runs"
    **Tuesday is lecture. Thursday and Friday are exercise sessions.** Every
    line of code in this course is written in the room, on the classroom
    network — join **cs326** and sign in once per laptop at
    [signin.cs326](guides/classroom-network.md). Read the **Prep** page before
    each session. The session's
    exercise is released when the session starts; run `oslings submit`
    before you leave, passed or not. **SUBMIT** lists what each session
    releases.

    Did not finish? Finish it yourself: Thursday's exercise by Thursday
    11:59 pm, Friday's by Monday 11:59 pm.

---

*Last updated: {{ now().strftime('%B %d, %Y') }}*
