import unittest
from db.models import Server, PingResult, PingLog, AlertLog, AppSetting
from db.init_db import init_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class TestDatabaseModels(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        self.Session = sessionmaker(bind=self.engine)
        
        # Create tables
        from db.models import Base
        Base.metadata.create_all(self.engine)
        
        self.session = self.Session()

    def tearDown(self):
        self.session.close()

    def test_server_model(self):
        # Test creating a server
        server = Server(
            name="Test Server",
            ip_address="192.168.1.100",
            ping_interval=30,
            is_active=True
        )
        
        self.session.add(server)
        self.session.commit()
        
        # Verify the server was saved
        saved_server = self.session.query(Server).first()
        self.assertIsNotNone(saved_server)
        self.assertEqual(saved_server.name, "Test Server")
        self.assertEqual(saved_server.ip_address, "192.168.1.100")
        self.assertEqual(saved_server.ping_interval, 30)
        self.assertTrue(saved_server.is_active)

    def test_ping_result_model(self):
        # Create a server first
        server = Server(
            name="Test Server",
            ip_address="192.168.1.100"
        )
        self.session.add(server)
        self.session.commit()
        
        # Create a ping result
        ping_result = PingResult(
            server_id=server.id,
            is_successful=True,
            latency_ms=25.5
        )
        
        self.session.add(ping_result)
        self.session.commit()
        
        # Verify the ping result
        saved_ping = self.session.query(PingResult).first()
        self.assertIsNotNone(saved_ping)
        self.assertTrue(saved_ping.is_successful)
        self.assertEqual(saved_ping.latency_ms, 25.5)
        self.assertEqual(saved_ping.server_id, server.id)

    def test_ping_log_model(self):
        # Create a server first
        server = Server(
            name="Test Server",
            ip_address="192.168.1.100"
        )
        self.session.add(server)
        self.session.commit()
        
        # Create a ping log
        ping_log = PingLog(
            server_id=server.id,
            response_time=30.5,
            success=True
        )
        
        self.session.add(ping_log)
        self.session.commit()
        
        # Verify the ping log
        saved_log = self.session.query(PingLog).first()
        self.assertIsNotNone(saved_log)
        self.assertTrue(saved_log.success)
        self.assertEqual(saved_log.response_time, 30.5)
        self.assertEqual(saved_log.server_id, server.id)

    def test_alert_log_model(self):
        # Create a server first
        server = Server(
            name="Test Server",
            ip_address="192.168.1.100"
        )
        self.session.add(server)
        self.session.commit()
        
        # Create an alert log
        alert_log = AlertLog(
            server_id=server.id,
            alert_type="downtime",
            message="Server is down"
        )
        
        self.session.add(alert_log)
        self.session.commit()
        
        # Verify the alert log
        saved_alert = self.session.query(AlertLog).first()
        self.assertIsNotNone(saved_alert)
        self.assertEqual(saved_alert.alert_type, "downtime")
        self.assertEqual(saved_alert.message, "Server is down")
        self.assertEqual(saved_alert.server_id, server.id)

    def test_app_setting_model(self):
        # Create an app setting
        app_setting = AppSetting(
            key="agent_status",
            value="running"
        )
        
        self.session.add(app_setting)
        self.session.commit()
        
        # Verify the app setting
        saved_setting = self.session.query(AppSetting).first()
        self.assertIsNotNone(saved_setting)
        self.assertEqual(saved_setting.key, "agent_status")
        self.assertEqual(saved_setting.value, "running")

    def test_relationships(self):
        # Test server relationships
        server = Server(
            name="Test Server",
            ip_address="192.168.1.100"
        )
        self.session.add(server)
        self.session.commit()
        
        # Create related objects
        ping_result = PingResult(
            server_id=server.id,
            is_successful=True,
            latency_ms=25.5
        )
        ping_log = PingLog(
            server_id=server.id,
            response_time=30.5,
            success=True
        )
        alert_log = AlertLog(
            server_id=server.id,
            alert_type="downtime",
            message="Server is down"
        )
        
        self.session.add(ping_result)
        self.session.add(ping_log)
        self.session.add(alert_log)
        self.session.commit()
        
        # Verify relationships
        saved_server = self.session.query(Server).first()
        self.assertIsNotNone(saved_server.ping_result)
        self.assertIsNotNone(saved_server.ping_logs)
        self.assertIsNotNone(saved_server.alerts)
        
        self.assertEqual(len(saved_server.ping_logs), 1)
        self.assertEqual(len(saved_server.alerts), 1)
        self.assertEqual(saved_server.ping_result.server_id, server.id)

if __name__ == '__main__':
    unittest.main()
