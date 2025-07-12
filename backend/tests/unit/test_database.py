"""Unit tests for the database module."""
import os
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, DatabaseError

from app.database import (
    DatabaseConfig,
    init_database,
    get_db_session,
    close_database
)


class TestDatabaseConfig:
    """Test cases for DatabaseConfig class."""

    def test_from_env_success(self):
        """Test successful creation from environment variables."""
        with patch.dict(os.environ, {
            'USERNAME': 'testuser',
            'PASS': 'testpass',
            'URL': 'localhost:5432',
            'DB': 'testdb'
        }):
            config = DatabaseConfig.from_env()
            assert config.username == 'testuser'
            assert config.password == 'testpass'
            assert config.url == 'localhost:5432'
            assert config.database == 'testdb'

    def test_from_env_missing_single_variable(self):
        """Test error when a single environment variable is missing."""
        with patch.dict(os.environ, {
            'USERNAME': 'testuser',
            'PASS': 'testpass',
            'URL': 'localhost:5432'
            # DB is missing
        }, clear=True):
            with pytest.raises(RuntimeError, match="Missing required environment variables: DB"):
                DatabaseConfig.from_env()

    def test_from_env_missing_multiple_variables(self):
        """Test error when multiple environment variables are missing."""
        with patch.dict(os.environ, {
            'USERNAME': 'testuser'
            # PASS, URL, DB are missing
        }, clear=True):
            with pytest.raises(RuntimeError, match="Missing required environment variables: PASS, URL, DB"):
                DatabaseConfig.from_env()

    def test_from_env_all_missing(self):
        """Test error when all environment variables are missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError, match="Missing required environment variables: USERNAME, PASS, URL, DB"):
                DatabaseConfig.from_env()

    def test_database_url_property(self):
        """Test database URL generation."""
        config = DatabaseConfig(
            username='testuser',
            password='testpass',
            url='localhost:5432',
            database='testdb'
        )
        assert config.database_url == 'postgresql://testuser:testpass@localhost:5432/testdb'

    def test_database_url_with_special_characters(self):
        """Test database URL with special characters in password."""
        config = DatabaseConfig(
            username='testuser',
            password='test@pass#123',
            url='localhost:5432',
            database='testdb'
        )
        assert config.database_url == 'postgresql://testuser:test@pass#123@localhost:5432/testdb'


class TestInitDatabase:
    """Test cases for init_database function."""

    @patch('app.database.sessionmaker')
    @patch('app.database.create_engine')
    def test_init_database_success(self, mock_create_engine, mock_sessionmaker):
        """Test successful database initialization."""
        # Setup
        config = DatabaseConfig(
            username='testuser',
            password='testpass',
            url='localhost:5432',
            database='testdb'
        )
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_session_factory = Mock()
        mock_sessionmaker.return_value = mock_session_factory

        # Execute
        init_database(config)

        # Verify
        mock_create_engine.assert_called_once_with(
            'postgresql://testuser:testpass@localhost:5432/testdb',
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True
        )
        mock_sessionmaker.assert_called_once_with(
            bind=mock_engine,
            expire_on_commit=False
        )

        # Check global variables were set
        import app.database
        assert app.database.engine == mock_engine
        assert app.database.session_maker == mock_session_factory

    @patch('app.database.sessionmaker')
    @patch('app.database.create_engine')
    def test_init_database_with_different_config(self, mock_create_engine, mock_sessionmaker):
        """Test database initialization with different configurations."""
        # Setup
        config = DatabaseConfig(
            username='admin',
            password='secret123',
            url='db.example.com:5432',
            database='production'
        )

        # Execute
        init_database(config)

        # Verify
        mock_create_engine.assert_called_once_with(
            'postgresql://admin:secret123@db.example.com:5432/production',
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True
        )

    @patch('app.database.create_engine')
    def test_init_database_engine_creation_error(self, mock_create_engine):
        """Test error handling when engine creation fails."""
        # Setup
        config = DatabaseConfig(
            username='testuser',
            password='testpass',
            url='localhost:5432',
            database='testdb'
        )
        mock_create_engine.side_effect = OperationalError("Cannot connect", None, None)

        # Execute and verify
        with pytest.raises(OperationalError):
            init_database(config)


class TestGetDbSession:
    """Test cases for get_db_session dependency function."""

    def test_get_db_session_success(self):
        """Test successful session creation and cleanup."""
        # Setup
        mock_session = Mock(spec=Session)
        mock_session_factory = Mock(return_value=mock_session)

        # Patch the global session_maker
        with patch('app.database.session_maker', mock_session_factory):
            # Execute
            generator = get_db_session()
            session = next(generator)

            # Verify session was created
            assert session == mock_session
            mock_session_factory.assert_called_once()

            # Verify session is not closed yet
            mock_session.close.assert_not_called()

            # Complete the generator
            with pytest.raises(StopIteration):
                next(generator)

            # Verify session was closed
            mock_session.close.assert_called_once()

    def test_get_db_session_with_exception(self):
        """Test session cleanup when exception occurs during usage."""
        # Setup
        mock_session = Mock(spec=Session)
        mock_session_factory = Mock(return_value=mock_session)

        # Patch the global session_maker
        with patch('app.database.session_maker', mock_session_factory):
            # Execute
            generator = get_db_session()
            _ = next(generator)

            # Simulate an exception during session usage
            try:
                generator.throw(ValueError("Test error"))
            except ValueError:
                pass

            # Verify session was still closed
            mock_session.close.assert_called_once()

    def test_get_db_session_when_not_initialized(self):
        """Test error when session_maker is not initialized."""
        # Patch session_maker to be None
        with patch('app.database.session_maker', None):
            with pytest.raises(RuntimeError, match="Database not initialized"):
                generator = get_db_session()
                next(generator)

    def test_get_db_session_multiple_calls(self):
        """Test multiple calls create different sessions."""
        # Setup
        mock_session1 = Mock(spec=Session)
        mock_session2 = Mock(spec=Session)
        mock_session_factory = Mock(side_effect=[mock_session1, mock_session2])

        # Patch the global session_maker
        with patch('app.database.session_maker', mock_session_factory):
            # Execute first call
            gen1 = get_db_session()
            session1 = next(gen1)

            # Execute second call
            gen2 = get_db_session()
            session2 = next(gen2)

            # Verify different sessions
            assert session1 != session2
            assert mock_session_factory.call_count == 2

            # Cleanup
            try:
                next(gen1)
            except StopIteration:
                pass
            try:
                next(gen2)
            except StopIteration:
                pass

            # Verify both sessions were closed
            mock_session1.close.assert_called_once()
            mock_session2.close.assert_called_once()


class TestCloseDatabase:
    """Test cases for close_database function."""

    def test_close_database_with_engine(self):
        """Test closing database when engine exists."""
        # Setup
        mock_engine = Mock()

        # Patch the global engine
        with patch('app.database.engine', mock_engine):
            # Execute
            close_database()

            # Verify
            mock_engine.dispose.assert_called_once()

    def test_close_database_without_engine(self):
        """Test closing database when engine is None."""
        # Patch the global engine to be None
        with patch('app.database.engine', None):
            # Execute - should not raise any errors
            close_database()

    def test_close_database_with_dispose_error(self):
        """Test error handling when engine.dispose() fails."""
        # Setup
        mock_engine = Mock()
        mock_engine.dispose.side_effect = DatabaseError("Dispose failed", None, None)

        # Patch the global engine
        with patch('app.database.engine', mock_engine):
            # Execute and verify error propagates
            with pytest.raises(DatabaseError):
                close_database()

            # Verify dispose was still called
            mock_engine.dispose.assert_called_once()


class TestIntegration:
    """Integration tests for the database module."""

    @patch('app.database.sessionmaker')
    @patch('app.database.create_engine')
    def test_full_lifecycle(self, mock_create_engine, mock_sessionmaker):
        """Test complete lifecycle: init -> use -> close."""
        # Setup
        config = DatabaseConfig(
            username='testuser',
            password='testpass',
            url='localhost:5432',
            database='testdb'
        )
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_session = Mock(spec=Session)
        mock_session_factory = Mock(return_value=mock_session)
        mock_sessionmaker.return_value = mock_session_factory

        # Initialize database
        init_database(config)

        # Use session
        with patch('app.database.session_maker', mock_session_factory):
            generator = get_db_session()
            session = next(generator)
            assert session == mock_session

            # Complete session usage
            try:
                next(generator)
            except StopIteration:
                pass

        # Close database
        with patch('app.database.engine', mock_engine):
            close_database()

        # Verify all operations
        mock_create_engine.assert_called_once()
        mock_sessionmaker.assert_called_once()
        mock_session_factory.assert_called_once()
        mock_session.close.assert_called_once()
        mock_engine.dispose.assert_called_once()

    def test_generator_cleanup_with_for_loop(self):
        """Test using get_db_session in a for loop (common FastAPI pattern)."""
        # Setup
        mock_session = Mock(spec=Session)
        mock_session_factory = Mock(return_value=mock_session)

        # Patch the global session_maker
        with patch('app.database.session_maker', mock_session_factory):
            # Use in for loop (common pattern in FastAPI dependencies)
            sessions = []
            for session in get_db_session():
                sessions.append(session)
                assert session == mock_session
                mock_session.close.assert_not_called()

            # Verify session was closed after loop
            mock_session.close.assert_called_once()
            assert len(sessions) == 1

    def test_error_recovery_scenario(self):
        """Test recovery after database errors."""
        # Setup initial state
        config = DatabaseConfig(
            username='testuser',
            password='testpass',
            url='localhost:5432',
            database='testdb'
        )

        # First attempt fails
        with patch('app.database.create_engine') as mock_create_engine:
            mock_create_engine.side_effect = OperationalError("Connection failed", None, None)

            with pytest.raises(OperationalError):
                init_database(config)

        # Second attempt succeeds
        with patch('app.database.create_engine') as mock_create_engine:
            with patch('app.database.sessionmaker') as mock_sessionmaker:
                mock_engine = Mock()
                mock_create_engine.return_value = mock_engine
                mock_create_engine.side_effect = None

                # Should work now
                init_database(config)

                # Verify recovery
                mock_create_engine.assert_called_once()
                mock_sessionmaker.assert_called_once()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string_environment_variables(self):
        """Test handling of empty string environment variables."""
        with patch.dict(os.environ, {
            'USERNAME': '',
            'PASS': '',
            'URL': '',
            'DB': ''
        }):
            with pytest.raises(RuntimeError, match="Missing required environment variables: USERNAME, PASS, URL, DB"):
                DatabaseConfig.from_env()

    def test_whitespace_environment_variables(self):
        """Test environment variables with only whitespace."""
        with patch.dict(os.environ, {
            'USERNAME': '   ',
            'PASS': '\t',
            'URL': '\n',
            'DB': ' \t\n'
        }):
            # Should create config but with whitespace values
            config = DatabaseConfig.from_env()
            assert config.username == '   '
            assert config.password == '\t'
            assert config.url == '\n'
            assert config.database == ' \t\n'

    @patch('app.database.sessionmaker')
    @patch('app.database.create_engine')
    def test_reinitialize_database(self, mock_create_engine, mock_sessionmaker):
        """Test reinitializing database multiple times."""
        config = DatabaseConfig(
            username='testuser',
            password='testpass',
            url='localhost:5432',
            database='testdb'
        )

        # First initialization
        mock_engine1 = Mock()
        mock_create_engine.return_value = mock_engine1
        init_database(config)

        # Second initialization (should overwrite)
        mock_engine2 = Mock()
        mock_create_engine.return_value = mock_engine2
        init_database(config)

        # Verify both calls were made
        assert mock_create_engine.call_count == 2
        assert mock_sessionmaker.call_count == 2

        # Verify current engine is the second one
        import app.database
        assert app.database.engine == mock_engine2
