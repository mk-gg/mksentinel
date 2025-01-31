from datetime import datetime, timezone
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# For Discord
class Member(db.Model):
    __tablename__ = 'member'
    member_id = db.Column(db.String(20), primary_key=True)
    username = db.Column(db.String(50), nullable=False)  # Current username at time of ban
    display_name = db.Column(db.String(50), nullable=True)  # Current display name at time of ban

    def to_json(self):
        return {
            'memberId': self.member_id,
            'username': self.username,
            'displayName': self.display_name
        }

class Server(db.Model):
    __tablename__ = 'server'
    server_id = db.Column(db.String(20), primary_key=True)
    server_name = db.Column(db.String(50), nullable=False)

    def to_json(self):
        return {
            'serverId': self.server_id,
            'serverName': self.server_name
        }

class Bans(db.Model):
    __tablename__ = 'bans'
    ban_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.String(20), db.ForeignKey('member.member_id'), nullable=False)
    server_id = db.Column(db.String(20), db.ForeignKey('server.server_id'), nullable=False)
    reason = db.Column(db.String(200), nullable=True)
    captured_message = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_json(self):
        return {
            'banId': self.ban_id,
            'memberId': self.member_id,
            'serverId': self.server_id,
            'reason': self.reason,
            'capturedMessage': self.captured_message,
            'createdAt': self.created_at.isoformat() if self.created_at else None
            
        }
