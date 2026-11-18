import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('coverage', Path(__file__).parents[1] / 'scripts/check_visual_coverage.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class VisualCoverageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='article coverage ')
        self.work = Path(self.tmp.name)
        self.article = self.work / '正文.md'
        self.article.write_text('# 作者的经验\n\n## 实践\n已有口述，先做文字阶段。', encoding='utf-8')
        self.shot = self.work / '手机审看证据.txt'
        self.shot.write_text('fixture evidence; not an actual visual approval', encoding='utf-8')
        self.plan = self.work / 'coverage.json'
        self.data = {
            'articleSha256': module.sha(self.article),
            'inventorySources': [],
            'noExistingAssetsReason': '本任务没有其他形态或用户素材，已检查作品目录',
            'candidates': [],
            'usedAssets': [],
            'anchors': [{'meaning': '个人实践', 'section': '实践', 'assets': [], 'textOnlyReason': '该段描述作者思考，没有需展示的机制或证据'}],
            'mobileReview': {'status': 'reviewed', 'findings': '测试记录，不代表实际作品通过', 'screenshots': [{'path': self.shot.name, 'sha256': module.sha(self.shot), 'viewportWidth': 390}]},
        }

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self):
        self.plan.write_text(json.dumps(self.data, ensure_ascii=False), encoding='utf-8')
        return module.check(self.work, self.article, self.plan)

    def test_does_not_force_generation_or_gif_without_visual_need(self):
        self.assertTrue(self.run_check()['passed'])

    def test_inventory_may_not_only_list_selected_assets(self):
        source = self.work / '视频素材.json'
        source.write_text(json.dumps({'assets': [{'id': 'selected'}, {'id': 'forgotten-motion'}]}), encoding='utf-8')
        self.data['inventorySources'] = [{'path': source.name, 'collection': 'assets', 'kind': 'material', 'sha256': module.sha(source)}]
        self.data['candidates'] = [{'key': source.name + '#selected', 'decision': 'not_used', 'reason': '不需要'}]
        result = self.run_check()
        self.assertFalse(result['passed'])
        self.assertTrue(any('forgotten-motion' in x for x in result['errors']))

    def test_missing_mobile_evidence_blocks_completion(self):
        self.data['mobileReview']['screenshots'] = []
        self.assertFalse(self.run_check()['passed'])

    def test_text_change_invalidates_review_binding(self):
        self.article.write_text(self.article.read_text(encoding='utf-8') + '\n新的主张', encoding='utf-8')
        self.assertFalse(self.run_check()['passed'])

    def test_user_approval_is_not_inferred(self):
        result = self.run_check()
        self.assertNotIn('userApproved', result)
        self.assertIn('不替代', result['scope'])

    def test_empty_anchor_section_is_rejected(self):
        self.data['anchors'] = [{'meaning': '空段落锚点绕过漏洞', 'section': '', 'assets': [], 'textOnlyReason': '纯文字'}]
        result = self.run_check()
        self.assertFalse(result['passed'])
        self.assertIn('重点无对应正文段落', result['errors'])

    def test_fenced_code_block_image_syntax_is_ignored(self):
        self.article.write_text(
            '# 作者的经验\n\n## 实践\n示例代码块：\n\n```markdown\n![示例语法](assets/not-a-real-file.png)\n```\n',
            encoding='utf-8',
        )
        self.data['articleSha256'] = module.sha(self.article)
        result = self.run_check()
        self.assertTrue(result['passed'], result['errors'])
        self.assertEqual(result['embeddedImages'], 0)

    def test_image_link_with_optional_title_is_resolved(self):
        img = self.work / 'step 1.png'
        img.write_bytes(b'PNGDATA')
        self.article.write_text(
            '# 作者的经验\n\n## 实践\n![图注：步骤说明](step%201.png "可选标题")\n',
            encoding='utf-8',
        )
        self.data['articleSha256'] = module.sha(self.article)
        self.data['candidates'] = [{'key': 'manual#1', 'decision': 'used', 'reason': '展示界面', 'outputs': [img.name], 'reviewEvidence': self.shot.name}]
        self.data['usedAssets'] = [{'path': img.name, 'sha256': module.sha(img)}]
        self.data['anchors'] = [{'meaning': '个人实践', 'section': '实践', 'assets': [img.name]}]
        result = self.run_check()
        self.assertTrue(result['passed'], result['errors'])
        self.assertEqual(result['embeddedImages'], 1)

    def test_missing_collection_key_reports_clear_error(self):
        source = self.work / '共享清单.json'
        source.write_text(json.dumps({'assets': [{'id': 'a1'}]}), encoding='utf-8')
        self.data['inventorySources'] = [{'path': source.name, 'sha256': module.sha(source)}]
        result = self.run_check()
        self.assertFalse(result['passed'])
        self.assertTrue(any('缺少有效 collection 字段' in x for x in result['errors']))


if __name__ == '__main__':
    unittest.main()
