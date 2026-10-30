#!/usr/bin/env python3
"""Generate and publish one Kubeify post. Run through cron_publish.sh."""
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.request
from zoneinfo import ZoneInfo
from banner import generate

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
TOPICS = json.loads((HERE / 'topics.json').read_text())
MODEL = os.environ.get('OPENCODE_MODEL', 'opencode/big-pickle')
OPENCODE = os.environ.get('OPENCODE_BIN', str(Path.home() / '.opencode/bin/opencode'))


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, text=True, capture_output=True).stdout.strip()


def slugify(title):
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')


def call_model(prompt):
    result = subprocess.run([OPENCODE, 'run', '--pure', '--model', MODEL, '--format', 'json', '--title', 'kubeify-blog', prompt], cwd=HERE, capture_output=True, text=True, timeout=600, check=True)
    parts = []
    for line in result.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get('type') == 'error':
            raise RuntimeError(str(event.get('error')))
        if event.get('type') == 'text':
            parts.append(event.get('part', {}).get('text', ''))
    if not parts:
        raise RuntimeError('OpenCode returned no text: ' + result.stderr)
    return ''.join(parts).strip()


def validate(body):
    prose = re.sub(r'```[\s\S]*?```', '', body)
    words = len(re.findall(r"\b[\w]+(?:['’-][\w]+)*\b", prose))
    if not 1200 <= words <= 1600:
        raise ValueError(f'Article has {words} prose words; expected 1200–1600')
    if not re.search(r'(?im)^## .*frequently asked questions|^## FAQ', body):
        raise ValueError('FAQ missing')
    if 'https://kubeify.com/contact' not in body:
        raise ValueError('Contact CTA missing')
    urls = set(re.findall(r'\]\((https://[^\s)]+)\)', body)) - {'https://kubeify.com/contact'}
    if len(urls) < 2:
        raise ValueError('At least two linked sources are required')
    for url in urls:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 KubeifyBlog/1.0'})
        with urllib.request.urlopen(req, timeout=20) as response:
            if response.status != 200:
                raise ValueError(f'Source not accessible: {url}')
    return words


def main():
    today = dt.datetime.now(ZoneInfo('Asia/Kolkata')).date().isoformat()
    # A failed push leaves the generated post committed locally. Retry it rather
    # than writing another post or accidentally publishing unrelated work.
    pending = HERE / '.pending.json'
    if pending.exists():
        data = json.loads(pending.read_text())
        post, image = ROOT / data['post'], ROOT / data['image']
        if not post.is_file() or not image.is_file():
            raise RuntimeError('Pending post or image missing; inspect .pending.json')
    else:
        if git('branch', '--show-current') != 'main':
            raise RuntimeError('Checkout must be on main')
        git('fetch', 'origin', 'main')
        if git('rev-parse', 'HEAD') != git('rev-parse', 'origin/main'):
            raise RuntimeError('Local main differs from origin/main; synchronize it before publishing')
        used = {p.name[11:-3] for p in (ROOT / '_posts').glob('????-??-??-*.md')}
        title = next((t for t in TOPICS if slugify(t) not in used), None)
        if not title:
            existing = [p.name for p in (ROOT / '_posts').glob('*.md')]
            title = call_model('Propose one specific practical article title for business owners on DevOps, Kubernetes, AIOps, MLOps or AI agent security, deployment, performance or cost. Avoid these existing posts: ' + json.dumps(existing) + '. Return only a title, no quotes or numbering. Do not claim it is trending without evidence.').strip(' "\'')
            if not title or len(title) > 150 or '\n' in title or slugify(title) in used:
                raise RuntimeError('Generated topic invalid or already used')
        slug = slugify(title)
        post = ROOT / '_posts' / f'{today}-{slug}.md'
        image = ROOT / 'images' / 'blog' / f'{slug}.webp'
        if post.exists() or image.exists():
            raise RuntimeError('Destination already exists')
        prompt = f'''Write a complete 1300-1500 word Markdown article titled "{title}" for Kubeify. Readers are business owners building DevOps and reducing cost; explain business impact and include practical technical detail. Use clear, natural human prose, no invented experiences, case studies, statistics, claims of customer results, or product features. Discuss concrete tradeoffs, security, costs and actionable decisions. Include a Frequently Asked Questions section and end with a natural CTA linking https://kubeify.com/contact. Link to at least two real, authoritative primary-source documentation pages that directly support technical claims; do not invent URLs. Do not make claims about current trends without dated verifiable evidence. Do not include YAML front matter or a top-level title. Return only the article body, no prefatory commentary. Target 1300-1500 prose words excluding code.'''
        last_error = None
        for _ in range(3):
            body = call_model(prompt + (f' Previous draft failed validation: {last_error}. Correct that.' if last_error else ''))
            try:
                count = validate(body)
                break
            except (ValueError, OSError) as exc:
                last_error = str(exc)
                print(f'Draft rejected: {exc}', flush=True)
        else:
            raise RuntimeError(f'No valid draft after three attempts: {last_error}')
        title_yaml = json.dumps(title, ensure_ascii=False)
        front = f'---\ntitle: {title_yaml}\ndescription: {json.dumps("A practical business guide to " + title.lower(), ensure_ascii=False)}\nimage: /images/blog/{slug}.webp\nlayout: post\npermalink: blog/:title\nauthor: Shyam\ncategory: Kubernetes\ndate: {today}T10:00:00+05:30\n---\n\n'
        generate(title, image)
        post.write_text(front + body + '\n', encoding='utf-8')
        pending.write_text(json.dumps({'post': str(post.relative_to(ROOT)), 'image': str(image.relative_to(ROOT))}))
        print(f'Created {post.name}: {count} prose words', flush=True)
    paths = [str(post.relative_to(ROOT)), str(image.relative_to(ROOT))]
    if git('branch', '--show-current') != 'main':
        raise RuntimeError('Checkout must be on main')
    # Refuse to include any staged work belonging to another process.
    staged = git('diff', '--cached', '--name-only').splitlines()
    if any(path not in paths for path in staged):
        raise RuntimeError('Unrelated staged changes found; resolve before publishing')
    git('add', '--', *paths)
    if git('diff', '--cached', '--name-only'):
        git('commit', '-m', f'Add Kubeify blog post for {today}', '--', *paths)
    git('fetch', 'origin', 'main')
    if subprocess.run(['git', 'merge-base', '--is-ancestor', 'origin/main', 'HEAD'], cwd=ROOT).returncode:
        raise RuntimeError('Remote main has changed; synchronize before retrying')
    changed = set(git('diff', '--name-only', 'origin/main..HEAD').splitlines())
    if changed and changed != set(paths):
        raise RuntimeError('Unpushed changes include unrelated files; inspect before retrying')
    git('push', 'origin', 'main')
    pending.unlink()
    print('Published to GitHub:', post.name, flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Publishing failed: {exc}', file=sys.stderr)
        sys.exit(1)
