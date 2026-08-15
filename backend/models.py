import json
from datetime import datetime
from backend.database import db

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='PENDING') # PENDING, RUNNING, READY, FAILED, REPAIR_REQUIRED
    current_stage = db.Column(db.String(50), default='pending')
    progress_pct = db.Column(db.Integer, default=0)
    frontend_port = db.Column(db.Integer, nullable=True)
    backend_port = db.Column(db.Integer, nullable=True)
    preview_url = db.Column(db.String(255), nullable=True)
    project_path = db.Column(db.String(500), nullable=True)
    requirements_spec_json = db.Column(db.Text, nullable=True)
    plan_spec_json = db.Column(db.Text, nullable=True)
    validation_report_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    logs = db.relationship('AgentLog', backref='project', cascade='all, delete-orphan', lazy=True, order_by='AgentLog.id.asc()')
    generation_runs = db.relationship('GenerationRun', backref='project', cascade='all, delete-orphan', lazy=True)
    deployments = db.relationship('DeploymentRecord', backref='project', cascade='all, delete-orphan', lazy=True)

    @property
    def requirements_spec(self):
        if self.requirements_spec_json:
            try:
                return json.loads(self.requirements_spec_json)
            except Exception:
                return None
        return None

    @requirements_spec.setter
    def requirements_spec(self, value):
        self.requirements_spec_json = json.dumps(value) if value is not None else None

    @property
    def plan_spec(self):
        if self.plan_spec_json:
            try:
                return json.loads(self.plan_spec_json)
            except Exception:
                return None
        return None

    @plan_spec.setter
    def plan_spec(self, value):
        self.plan_spec_json = json.dumps(value) if value is not None else None

    @property
    def validation_report(self):
        if self.validation_report_json:
            try:
                return json.loads(self.validation_report_json)
            except Exception:
                return None
        return None

    @validation_report.setter
    def validation_report(self, value):
        self.validation_report_json = json.dumps(value) if value is not None else None

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "prompt": self.prompt,
            "description": self.description,
            "status": self.status,
            "current_stage": self.current_stage,
            "progress_pct": self.progress_pct,
            "frontend_port": self.frontend_port,
            "backend_port": self.backend_port,
            "preview_url": self.preview_url,
            "project_path": self.project_path,
            "requirements_spec": self.requirements_spec,
            "plan_spec": self.plan_spec,
            "validation_report": self.validation_report,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class GenerationRun(db.Model):
    __tablename__ = 'generation_runs'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    status = db.Column(db.String(50), default='RUNNING')
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)
    repair_attempts = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "repair_attempts": self.repair_attempts,
            "error_message": self.error_message,
        }


class AgentLog(db.Model):
    __tablename__ = 'agent_logs'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    stage = db.Column(db.String(50), nullable=False) # requirement, planning, coding, database, testing, repair, documentation, validation
    level = db.Column(db.String(20), default='INFO') # INFO, SUCCESS, WARNING, ERROR
    message = db.Column(db.Text, nullable=False)
    details_json = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def details(self):
        if self.details_json:
            try:
                return json.loads(self.details_json)
            except Exception:
                return self.details_json
        return None

    @details.setter
    def details(self, value):
        if isinstance(value, (dict, list)):
            self.details_json = json.dumps(value)
        elif value is not None:
            self.details_json = str(value)
        else:
            self.details_json = None

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "stage": self.stage,
            "level": self.level,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class DeploymentRecord(db.Model):
    __tablename__ = 'deployment_records'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    target = db.Column(db.String(50), nullable=False) # vercel, render
    status = db.Column(db.String(50), default='PENDING') # PENDING, IN_PROGRESS, SUCCESS, FAILED
    url = db.Column(db.String(500), nullable=True)
    logs = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "target": self.target,
            "status": self.status,
            "url": self.url,
            "logs": self.logs,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
