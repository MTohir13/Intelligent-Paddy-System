from supabase import create_client
import os
from dotenv import load_dotenv
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

load_dotenv()
logger = logging.getLogger(__name__)


class SupabaseDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseDB, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.url = os.getenv("SUPABASE_URL")
            self.key = os.getenv("SUPABASE_ANON_KEY")
            self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

            if not all([self.url, self.key, self.service_key]):
                raise ValueError("Missing Supabase credentials. Check your .env file.")

            self.client = create_client(self.url, self.key)
            self.service_client = create_client(self.url, self.service_key)
            self._initialized = True

    @property
    def auth(self):
        return self.client.auth

    def query(self, table: str, use_service_role: bool = False):
        client = self.service_client if use_service_role else self.client
        return client.table(table)

    # =========================================================
    # ROLE HELPERS
    # =========================================================
    def get_role_name(self, role_id: str) -> str:
        try:
            response = (
                self.query("user_roles", use_service_role=True)
                .select("role_name")
                .eq("id", role_id)
                .single()
                .execute()
            )
            if response.data:
                return response.data["role_name"]
            return "unknown"
        except Exception:
            return "unknown"

    def get_role_id(self, role_name: str) -> Optional[str]:
        try:
            response = (
                self.query("user_roles", use_service_role=True)
                .select("id")
                .eq("role_name", role_name)
                .single()
                .execute()
            )
            if response.data:
                return response.data["id"]
            return None
        except Exception:
            return None

    # =========================================================
    # USER HELPERS
    # =========================================================
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            response = (
                self.query("users", use_service_role=True)
                .select("*")
                .eq("email", email.lower())
                .single()
                .execute()
            )
            if not response.data:
                return None

            user = response.data
            user["role_name"] = self.get_role_name(user.get("role_id"))
            user["is_active"] = user.get("is_active", True)
            return user
        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {e}")
            return None

    def get_all_users(self) -> List[Dict[str, Any]]:
        try:
            response = (
                self.query("users", use_service_role=True)
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )

            users = response.data or []
            for user in users:
                user["role_name"] = self.get_role_name(user.get("role_id"))
                user["is_active"] = user.get("is_active", True)
            return users
        except Exception as e:
            logger.error(f"Error fetching all users: {e}")
            return []

    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        try:
            payload = dict(update_data)
            payload["updated_at"] = "now()"

            response = (
                self.query("users", use_service_role=True)
                .update(payload)
                .eq("id", user_id)
                .execute()
            )
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False

    def update_user_status(self, user_id: str, is_active: bool) -> bool:
        return self.update_user(user_id, {"is_active": is_active})

    # =========================================================
    # FARMERS + OFFICERS
    # =========================================================
    def get_all_farmers_with_users(self) -> List[Dict[str, Any]]:
        try:
            farmers_response = (
                self.query("farmers", use_service_role=True)
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )
            farmers = farmers_response.data or []

            users_response = (
                self.query("users", use_service_role=True)
                .select("*")
                .execute()
            )
            users = users_response.data or []
            user_map = {u["id"]: u for u in users}

            merged = []
            for farmer in farmers:
                user = user_map.get(farmer["id"], {})
                merged.append({
                    "id": farmer.get("id"),
                    "user_type": "farmer",
                    "code": farmer.get("farmer_id"),
                    "name": farmer.get("full_name") or user.get("full_name"),
                    "email": farmer.get("email") or user.get("email"),
                    "phone": user.get("phone"),
                    "region": farmer.get("region") or user.get("region"),
                    "area": farmer.get("area"),
                    "created_at": farmer.get("created_at") or user.get("created_at"),
                    "updated_at": farmer.get("updated_at") or user.get("updated_at"),
                    "last_login": user.get("last_login"),
                    "is_active": user.get("is_active", True),
                })
            return merged
        except Exception as e:
            logger.error(f"Error fetching farmers with users: {e}")
            return []

    def get_all_officers_with_users(self) -> List[Dict[str, Any]]:
        try:
            officers_response = (
                self.query("officers", use_service_role=True)
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )
            officers = officers_response.data or []

            users_response = (
                self.query("users", use_service_role=True)
                .select("*")
                .execute()
            )
            users = users_response.data or []
            user_map = {u["id"]: u for u in users}

            merged = []
            for officer in officers:
                user = user_map.get(officer["id"], {})
                merged.append({
                    "id": officer.get("id"),
                    "user_type": "officer",
                    "code": officer.get("officer_id"),
                    "name": officer.get("officer_name") or user.get("full_name"),
                    "email": officer.get("email") or user.get("email"),
                    "phone": officer.get("phone") or user.get("phone"),
                    "region": officer.get("region") or user.get("region"),
                    "area": "-",
                    "created_at": officer.get("created_at") or user.get("created_at"),
                    "updated_at": officer.get("updated_at") or user.get("updated_at"),
                    "last_login": user.get("last_login"),
                    "is_active": user.get("is_active", True),
                })
            return merged
        except Exception as e:
            logger.error(f"Error fetching officers with users: {e}")
            return []

    # =========================================================
    # DETECTION HISTORY
    # =========================================================
    def get_all_detection_history(self) -> List[Dict[str, Any]]:
        try:
            response = (
                self.query("detection_history", use_service_role=True)
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )
            return response.data or []
        except Exception as e:
            logger.error(f"Error fetching detection history: {e}")
            return []

    # =========================================================
    # COUNTS / DASHBOARD
    # =========================================================
    def get_system_stats(self) -> Dict[str, Any]:
        try:
            total_farmers = (
                self.query("farmers", use_service_role=True)
                .select("id", count="exact")
                .execute()
                .count or 0
            )

            total_officers = (
                self.query("officers", use_service_role=True)
                .select("id", count="exact")
                .execute()
                .count or 0
            )

            total_reports = (
                self.query("detection_history", use_service_role=True)
                .select("id", count="exact")
                .execute()
                .count or 0
            )

            total_users = (
                self.query("users", use_service_role=True)
                .select("id", count="exact")
                .execute()
                .count or 0
            )

            active_users = (
                self.query("users", use_service_role=True)
                .select("id", count="exact")
                .eq("is_active", True)
                .execute()
                .count or 0
            )

            suspended_users = total_users - active_users

            return {
                "total_farmers": total_farmers,
                "total_officers": total_officers,
                "total_reports": total_reports,
                "total_users": total_users,
                "active_users": active_users,
                "suspended_users": suspended_users,
                "last_updated": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {
                "total_farmers": 0,
                "total_officers": 0,
                "total_reports": 0,
                "total_users": 0,
                "active_users": 0,
                "suspended_users": 0,
                "last_updated": datetime.now().isoformat(),
            }

    # =========================================================
    # ACTIVITY LOGS
    # =========================================================
    def log_activity(
        self,
        user_id: Optional[str],
        email: Optional[str],
        action: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            payload = {
                "user_id": user_id,
                "email": email,
                "action": action,
                "description": description,
                "metadata": metadata if metadata else None,
            }
            self.query("activity_logs", use_service_role=True).insert(payload).execute()
            return True
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
            return False

    def get_activity_logs(self, limit: int = 200) -> List[Dict[str, Any]]:
        try:
            response = (
                self.query("activity_logs", use_service_role=True)
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data or []
        except Exception as e:
            logger.error(f"Error fetching activity logs: {e}")
            return []

    def get_officer_activity_logs(self, limit: int = 200) -> List[Dict[str, Any]]:
        try:
            response = (
                self.query("activity_logs_officer", use_service_role=True)
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data or []
        except Exception as e:
            logger.error(f"Error fetching officer activity logs: {e}")
            return []

    # =========================================================
    # LOGIN HELPER
    # =========================================================
    def login_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            user_data = self.get_user_by_email(email)

            if user_data and not user_data.get("is_active", True):
                logger.warning(f"Login blocked for suspended user: {email}")
                return None

            auth_response = self.auth.sign_in_with_password({
                "email": email.strip().lower(),
                "password": password
            })

            if auth_response.user:
                user_data = self.get_user_by_email(email)
                if user_data:
                    if not user_data.get("is_active", True):
                        return None

                    self.update_user(auth_response.user.id, {"last_login": "now()"})

                    return {
                        "id": auth_response.user.id,
                        "email": auth_response.user.email,
                        "full_name": user_data.get("full_name", ""),
                        "role_id": user_data.get("role_id"),
                        "role": user_data.get("role_name", "unknown"),
                        "phone": user_data.get("phone", ""),
                        "region": user_data.get("region", ""),
                        "is_active": user_data.get("is_active", True),
                    }
            return None
        except Exception as e:
            logger.error(f"Login error for {email}: {e}")
            return None


db = SupabaseDB()