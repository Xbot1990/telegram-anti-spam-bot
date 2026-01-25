# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime, timedelta
from config import CACHE_FILE

class Database:
    def __init__(self):
        self.data = self.load_cache()
    
    def load_cache(self):
        """Загружает данные из файла кэша"""
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Ошибка загрузки кэша: {e}")
                return self.create_empty_cache()
        return self.create_empty_cache()
    
    def create_empty_cache(self):
        """Создает пустую структуру данных"""
        return {
            "группы": {},
            "админы": {},
            "платежи": {},
            "нарушители": {}
        }
    
    def save_cache(self):
        """Сохраняет данные в файл"""
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения кэша: {e}")
            return False
    
    def get_admin(self, admin_id):
        """Получает информацию об админе"""
        return self.data["админы"].get(str(admin_id))
    
    def create_admin(self, admin_id, username="", first_name=""):
        """Создает нового админа"""
        admin_data = {
            "id": admin_id,
            "username": username,
            "first_name": first_name,
            "тариф": "trial",
            "окончание_подписки": (datetime.now() + timedelta(days=30)).isoformat(),
            "группы": [],
            "оплаты": []
        }
        self.data["админы"][str(admin_id)] = admin_data
        self.save_cache()
        return admin_data
    
    def update_admin_tariff(self, admin_id, tariff, period_days=30):
        """Обновляет тариф админа"""
        admin = self.get_admin(admin_id)
        if admin:
            admin["тариф"] = tariff
            admin["окончание_подписки"] = (datetime.now() + timedelta(days=period_days)).isoformat()
            self.save_cache()
    
    def add_admin_group(self, admin_id, group_id, group_title):
        """Добавляет группу админу"""
        admin = self.get_admin(admin_id)
        if admin:
            if not any(g["id"] == group_id for g in admin["группы"]):
                admin["группы"].append({"id": group_id, "title": group_title})
                self.save_cache()
    
    def get_group(self, group_id):
        """Получает информацию о группе"""
        return self.data["группы"].get(str(group_id))
    
    def create_group(self, group_id, group_title, admin_id):
        """Создает новую группу"""
        from config import DEFAULT_SETTINGS
        group_data = {
            "id": group_id,
            "title": group_title,
            "admin_id": admin_id,
            "настройки": DEFAULT_SETTINGS.copy()
        }
        self.data["группы"][str(group_id)] = group_data
        self.save_cache()
        return group_data
    
    def update_group_settings(self, group_id, settings):
        """Обновляет настройки группы"""
        group = self.get_group(group_id)
        if group:
            group["настройки"] = settings
            self.save_cache()
    
    def add_violation(self, group_id, user_id, reason, message_text=""):
        """Добавляет нарушение пользователя"""
        key = f"{group_id}_{user_id}"
        if key not in self.data["нарушители"]:
            self.data["нарушители"][key] = {"предупреждения": 0, "нарушения": []}
        
        violation = {
            "время": datetime.now().isoformat(),
            "причина": reason,
            "сообщение": message_text[:200]
        }
        self.data["нарушители"][key]["нарушения"].append(violation)
        self.data["нарушители"][key]["предупреждения"] += 1
        
        # Ограничиваем историю нарушений
        if len(self.data["нарушители"][key]["нарушения"]) > 3:
            self.data["нарушители"][key]["нарушения"] = self.data["нарушители"][key]["нарушения"][-3:]
        
        self.save_cache()
        return self.data["нарушители"][key]["предупреждения"]
    
    def get_violations(self, group_id, user_id):
        """Получает нарушения пользователя"""
        key = f"{group_id}_{user_id}"
        return self.data["нарушители"].get(key, {"предупреждения": 0, "нарушения": []})
    
    def reset_violations(self, group_id, user_id):
        """Сбрасывает нарушения пользователя"""
        key = f"{group_id}_{user_id}"
        if key in self.data["нарушители"]:
            del self.data["нарушители"][key]
            self.save_cache()
    
    def create_payment(self, admin_id, tariff, amount, period="month"):
        """Создает платеж"""
        payment_id = f"pay_{datetime.now().strftime('%Y%m%d%H%M%S')}_{admin_id}"
        payment_data = {
            "id": payment_id,
            "admin_id": admin_id,
            "тариф": tariff,
            "сумма": amount,
            "период": period,
            "статус": "ожидание",
            "создан": datetime.now().isoformat(),
            "скриншот": None
        }
        self.data["платежи"][payment_id] = payment_data
        self.save_cache()
        return payment_data
    
    def update_payment(self, payment_id, status, screenshot=None):
        """Обновляет статус платежа"""
        if payment_id in self.data["платежи"]:
            payment = self.data["платежи"][payment_id]
            payment["статус"] = status
            if screenshot:
                payment["скриншот"] = screenshot
            if status == "подтвержден":
                payment["подтвержден"] = datetime.now().isoformat()
            self.save_cache()
            return True
        return False

# Глобальный экземпляр базы данных
db = Database()
