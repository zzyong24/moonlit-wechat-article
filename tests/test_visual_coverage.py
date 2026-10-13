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
        self.article.write_text('# 作者的经验\n\n## 实践\n已有口述，先做文字阶段。')
        self.shot = self.work / '手机审看证据.txt'
        self.shot.write_text('fixture evidence; not an actual visual approval')
        self.plan = self.work / 'coverage.json'
        self.data = {'articleSha256': module.sha(self.article), 'inventorySources': [], 'noExistingAssetsReason': '本任务没有其他形态或用户素材，已检查作品目录', 'candidates': [], 'usedAssets': [], 'anchors': [{'meaning': '个人实践', 'section': '实践', 'assets': [], 'textOnlyReason': '该段描述作者思考，没有需展示的机制或证据'}], 'mobileReview': {'status': 'reviewed', 'findings': '测试记录，不代表实际作品通过', 'screenshots': [{'path': self.shot.name, 'sha256': module.sha(self.shot), 'viewportWidth': 390}]}}

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self):
        self.plan.write_text(json.dumps(self.data, ensure_ascii=False))
        return module.check(self.work, self.article, self.plan)

    def test_does_not_force_generation_or_gif_without_visual_need(self):
        self.assertTrue(self.run_check()['passed'])

    def test_inventory_may_not_only_list_selected_assets(self):
        source = self.work / '视频素材.json'
        source.write_text(json.dumps({'assets': [{'id': 'selected'}, {'id': 'forgotten-motion'}]}))
        self.data['inventorySources'] = [{'path': source.name, 'collection': 'assets', 'kind': 'material', 'sha256': module.sha(source)}]
        self.data['candidates'] = [{'key': source.name + '#selected', 'decision': 'not_used', 'reason': '不需要'}]
        result = self.run_check()
        self.assertFalse(result['passed'])
        self.assertTrue(any('forgotten-motion' in x for x in result['errors']))

    def test_missing_mobile_evidence_blocks_completion(self):
        self.data['mobileReview']['screenshots'] = []
        self.assertFalse(self.run_check()['passed'])

    def test_text_change_invalidates_review_binding(self):
        self.article.write_text(self.article.read_text() + '\n新的主张')
        self.assertFalse(self.run_check()['passed'])

    def test_user_approval_is_not_inferred(self):
        result = self.run_check()
        self.assertNotIn('userApproved', result)
        self.assertIn('不替代', result['scope'])


if __name__ == '__main__':
    unittest.main()
