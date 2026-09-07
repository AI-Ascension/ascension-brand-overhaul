import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('runtime_snapshot', Path(__file__).resolve().parents[1] / 'scripts/runtime_snapshot.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RuntimeSnapshotTests(unittest.TestCase):
    def test_tree_selection_excludes_unrelated_threads_and_private_text(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / 'metadata.sqlite'
            connection = sqlite3.connect(database)
            connection.execute('CREATE TABLE threads (id TEXT, source TEXT, model TEXT, reasoning_effort TEXT, agent_path TEXT, cli_version TEXT, created_at_ms INTEGER, title TEXT)')
            for name, parent, depth in [('root', None, 0), ('lead', 'root', 1), ('coordinator', 'lead', 2), ('leaf', 'coordinator', 3), ('unrelated', None, 0)]:
                source = json.dumps({'subagent': {'thread_spawn': {'parent_thread_id': parent, 'depth': depth}}}) if parent else 'cli'
                connection.execute('INSERT INTO threads VALUES (?,?,?,?,?,?,?,?)', (name, source, 'gpt-5.6-luna', 'max', '/'+name, 'test', depth, 'PRIVATE TEST TEXT'))
            connection.commit()
            connection.execute('UPDATE threads SET source = ? WHERE id = ?', ('{"subagent":"other-native-source"}', 'unrelated'))
            connection.commit()
            connection.close()
            result = module.snapshot(database, 'root')
            self.assertEqual({row['id'] for row in result['threads']}, {'root', 'lead', 'coordinator', 'leaf'})
            self.assertNotIn('PRIVATE TEST TEXT', json.dumps(result))
            self.assertEqual(next(row for row in result['threads'] if row['id'] == 'leaf')['parent_id'], 'coordinator')
            with self.assertRaisesRegex(ValueError, 'absent'):
                module.snapshot(database, 'missing')

    def test_missing_database_is_not_created(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / 'missing.sqlite'
            with self.assertRaises(sqlite3.OperationalError):
                module.snapshot(database, 'root')
            self.assertFalse(database.exists())
