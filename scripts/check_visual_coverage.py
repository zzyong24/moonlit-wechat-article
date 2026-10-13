#!/usr/bin/env python3
"""Check observable article visual work. This is not a semantic or aesthetic judge."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(work, markdown, plan):
    work, markdown = Path(work).resolve(), Path(markdown).resolve()
    data = json.loads(Path(plan).read_text())
    errors = []
    def file(ref):
        p = (work / ref).resolve()
        try:
            p.relative_to(work)
        except ValueError:
            errors.append('证据不在作品中：' + ref)
        if not p.is_file():
            errors.append('文件缺失：' + ref)
        return p
    if data.get('articleSha256') != sha(markdown):
        errors.append('覆盖记录没有绑定当前正文')
    sources = data.get('inventorySources', [])
    if not sources and not data.get('noExistingAssetsReason'):
        errors.append('缺少素材盘点来源或无现有素材的实际原因')
    expected = set()
    for source in sources:
        p = file(source['path'])
        if not p.is_file():
            continue
        if source.get('sha256') != sha(p):
            errors.append('素材盘点来源已变化：' + source['path'])
        manifest = json.loads(p.read_text())
        rows = manifest if source.get('collection') == '$' else manifest[source['collection']]
        for row in rows:
            identity = row.get('assetId') if source.get('kind') == 'motion' else row.get('asset_id', row.get('id', row.get('name')))
            expected.add(source['path'] + '#' + str(identity))
    candidates = data.get('candidates', [])
    found = {c['key'] for c in candidates}
    if expected - found:
        errors.append('遗漏素材候选：' + ', '.join(sorted(expected - found)))
    if len(found) != len(candidates):
        errors.append('候选ID重复')
    used = set()
    for c in candidates:
        if c.get('decision') not in ['used', 'adapted', 'not_used'] or not c.get('reason'):
            errors.append('候选未处理或缺原因：' + c['key'])
        if c.get('decision') in ['used', 'adapted']:
            for output in c.get('outputs', []):
                used.add(str(file(output)))
            if not c.get('outputs'):
                errors.append('选用候选无真实产物：' + c['key'])
            if not c.get('reviewEvidence'):
                errors.append('选用候选缺审看证据：' + c['key'])
            else:
                file(c['reviewEvidence'])
    embedded = {(markdown.parent / unquote(x.strip().strip('<>'))).resolve() for x in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', markdown.read_text())}
    if {str(p) for p in embedded} - used:
        errors.append('正文图片没有候选/生成记录映射')
    for p in embedded:
        if not p.is_file():
            errors.append('正文图片缺失：' + str(p))
    assets = {str((work / a['path']).resolve()): a for a in data.get('usedAssets', [])}
    for p in embedded:
        if p.is_file() and assets.get(str(p), {}).get('sha256') != sha(p):
            errors.append('图片未绑定当前hash：' + str(p))
    anchors = data.get('anchors', [])
    if not anchors:
        errors.append('没有作者重点与段落职责对应')
    for anchor in anchors:
        if not anchor.get('meaning') or anchor.get('section') not in markdown.read_text():
            errors.append('重点无对应正文段落')
        refs = anchor.get('assets', [])
        if not refs and not anchor.get('textOnlyReason'):
            errors.append('重点缺视觉或明确不配图的理由')
        if any(str((work / p).resolve()) not in {str(x) for x in embedded} for p in refs):
            errors.append('重点引用未嵌入正文的图片')
    mobile = data.get('mobileReview', {})
    if mobile.get('status') != 'reviewed' or not mobile.get('findings'):
        errors.append('缺少手机端实际审看结论')
    if not mobile.get('screenshots'):
        errors.append('缺少手机端截图证据')
    for shot in mobile.get('screenshots', []):
        p = file(shot['path'])
        if p.is_file() and shot.get('sha256') != sha(p):
            errors.append('手机端证据hash不符')
        if not 320 <= shot.get('viewportWidth', 0) <= 430:
            errors.append('审看宽度不是手机正文宽度')
    return {'passed': not errors, 'errors': errors, 'inventoryCandidates': len(expected), 'embeddedImages': len(embedded), 'scope': '只验证覆盖记录、文件与版本绑定；不替代视觉语义审读、审美、用户认可或发布风险审核。'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', required=True)
    p.add_argument('--markdown', required=True)
    p.add_argument('--plan', required=True)
    p.add_argument('--output')
    a = p.parse_args()
    try:
        result = check(a.work, a.markdown, a.plan)
    except (KeyError, ValueError, OSError, TypeError) as error:
        result = {'passed': False, 'errors': [str(error)]}
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if a.output:
        Path(a.output).write_text(text + '\n')
    print(text)
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
