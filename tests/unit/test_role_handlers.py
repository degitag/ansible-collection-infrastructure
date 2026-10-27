from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def task_notifications(tasks):
    for task in tasks:
        values = task.get('notify', [])
        yield from [values] if isinstance(values, str) else values
        for key in ('block', 'rescue', 'always'):
            yield from task_notifications(task.get(key, []))


def test_literal_notifications_resolve_to_handler_names_or_topics():
    known = set()
    for path in (ROOT / 'roles').glob('*/handlers/*.yml'):
        for task in yaml.safe_load(path.read_text()) or []:
            known.add(task['name'])
            listen = task.get('listen', [])
            known.update([listen] if isinstance(listen, str) else listen)
    unresolved = []
    for path in (ROOT / 'roles').glob('*/tasks/*.yml'):
        for notification in task_notifications(yaml.safe_load(path.read_text()) or []):
            if '{{' not in notification and notification not in known:
                unresolved.append(f'{path.relative_to(ROOT)}: {notification}')
    assert not unresolved, '\n'.join(unresolved)
