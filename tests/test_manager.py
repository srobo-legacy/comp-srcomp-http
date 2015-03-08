
import mock
import os.path

from sr.comp.http.manager import update_lock, LOCK_FILE

def test_update_lock():
    mock_excl_fd = mock.MagicMock()
    mock_excl_lock = mock.Mock(return_value = mock_excl_fd)

    with mock.patch('sr.comp.http.manager.exclusive_lock', mock_excl_lock), \
         mock.patch('sr.comp.http.manager.touch_update_file') as mock_touch:
        with update_lock('foo'):
            expected_lock_file = os.path.join('foo', LOCK_FILE)
            mock_excl_lock.assert_called_with(expected_lock_file)

            mock_excl_fd.__enter__.assert_called_with()

        assert mock_excl_fd.__exit__.called, "Failed to release the lock file"
        mock_touch.assert_called_with('foo')

def test_update_lock_when_exception():
    mock_excl_fd = mock.MagicMock()
    mock_excl_lock = mock.Mock(return_value = mock_excl_fd)

    class FakeError(Exception):
        pass

    with mock.patch('sr.comp.http.manager.exclusive_lock', mock_excl_lock), \
         mock.patch('sr.comp.http.manager.touch_update_file') as mock_touch:
        try:
            with update_lock('foo'):
                expected_lock_file = os.path.join('foo', LOCK_FILE)
                mock_excl_lock.assert_called_with(expected_lock_file)

                mock_excl_fd.__enter__.assert_called_with()

                raise FakeError()
        except FakeError:
            pass
        else:
            assert False, "Should have bubbled exception"

        assert mock_excl_fd.__exit__.called, "Failed to release the lock file"
        assert not mock_touch.called, "Should not touch the update file on failure"
