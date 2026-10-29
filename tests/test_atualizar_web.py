import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'SCRIPTS'))
import atualizar_web as updater

class DiscoveryTests(unittest.TestCase):
    def test_official_names_and_accents(self):
        for suffix, version in [(' - ALT_02', 'ALT-02'), (' - ALT_01', 'ALT-01'), (' ALT_1', 'ALT-01')]:
            self.assertEqual(updater.identify('Escala de Rodízio Única ZP-17', f'https://www.marinha.mil.br/EscalaDeRodizio_ZP17_10-2026{suffix}.pdf'), (2026, 10, version))

    def test_same_document_on_two_hosts(self):
        found = {}
        for host in ['www', 'assets']:
            updater.add_candidate(found, dict(year=2026, month=10, version='ALT-02', url=f'https://{host}.marinha.mil.br/a.pdf'))
        self.assertEqual(len(found), 1)

    def test_unavailable_page_must_not_report_success(self):
        with patch.object(updater, 'fetch', side_effect=URLError('offline')), patch.object(updater, 'existing_candidates', return_value=[]):
            with self.assertRaises(RuntimeError):
                updater.discover()

    def test_html_without_scales_must_not_report_success(self):
        with patch.object(updater, 'fetch', return_value=b'<html>Temporarily unavailable</html>'), patch.object(updater, 'existing_candidates', return_value=[]):
            with self.assertRaises(RuntimeError):
                updater.discover()

    def test_current_page_discovers_padded_alteration(self):
        html = b'<a href="/cppr/files/EscalaDeRodizio_ZP17_10-2026%20-%20ALT_02.pdf">Escala de Rodizio Unica ZP-17 - OUTUBRO - ALT 2</a>'
        with patch.object(updater, 'fetch', return_value=html), patch.object(updater, 'existing_candidates', return_value=[]):
            self.assertTrue(any(c['month'] == 10 and c['version'] == 'ALT-02' for c in updater.discover()))

if __name__ == '__main__':
    unittest.main()
