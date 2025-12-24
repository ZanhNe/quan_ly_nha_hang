from abc import ABC, abstractmethod
from typing import Any, Dict

class ThanhToanOnline(ABC):
    @abstractmethod
    def xu_ly_thanh_toan_online(self, so_tien: int, metadata) -> Dict[str, Any]:
        pass


    @abstractmethod
    def xac_thuc_webhook(self, payload, sig_header, endpoint_secret) -> Dict[str, Any]:
        pass